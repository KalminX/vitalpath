import logging
import json
from decimal import Decimal
import stripe
from django.conf import settings
from django.utils import timezone
from .models import Customer, Order, OrderItem, Payment, WebhookEvent
from apps.products.models import Product
from apps.notifications.services import send_purchase_confirmation

logger = logging.getLogger(__name__)

def get_stripe_client():
    if settings.STRIPE_SECRET_KEY:
        stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


class StripeCheckoutService:
    """
    Handles Stripe Checkout Session creation and webhook processing.
    """

    @classmethod
    def create_checkout_session(cls, product: Product, customer_email: str = None, request=None) -> dict:
        """
        Creates a Stripe Checkout Session for a one-time digital educational product.
        """
        base_url = settings.SITE_URL
        if request:
            base_url = request.build_absolute_uri('/')[:-1]

        success_url = f"{base_url}/checkout/success/?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{base_url}/checkout/cancel/?product_slug={product.slug}"

        get_stripe_client()

        # If Stripe is properly configured with a live or test key
        is_real_key = bool(settings.STRIPE_SECRET_KEY and not settings.STRIPE_SECRET_KEY.startswith('sk_test_sample'))

        if is_real_key:
            try:
                line_item = {
                    'price_data': {
                        'currency': product.currency.lower(),
                        'unit_amount': product.price_in_cents,
                        'product_data': {
                            'name': f"VitalPath: {product.title}",
                            'description': product.short_description[:200],
                        },
                    },
                    'quantity': 1,
                }

                session_params = {
                    'payment_method_types': ['card'],
                    'line_items': [line_item],
                    'mode': 'payment',
                    'success_url': success_url,
                    'cancel_url': cancel_url,
                    'client_reference_id': str(product.id),
                    'metadata': {
                        'product_id': str(product.id),
                        'product_slug': product.slug,
                        'product_title': product.title,
                    },
                }

                if customer_email:
                    session_params['customer_email'] = customer_email

                session = stripe.checkout.Session.create(**session_params)
                return {
                    'session_id': session.id,
                    'url': session.url,
                    'is_simulated': False
                }
            except Exception as e:
                logger.error(f"Stripe API error: {e}")
                # Fallback to simulated checkout flow for demonstration sandbox
                return cls._create_simulated_session(product, customer_email, base_url)
        else:
            return cls._create_simulated_session(product, customer_email, base_url)

    @classmethod
    def _create_simulated_session(cls, product: Product, customer_email: str = None, base_url: str = "http://127.0.0.1:8000") -> dict:
        """
        Creates a development/demonstration sandbox checkout session
        allowing full testing even without external internet Stripe credentials.
        """
        import uuid
        mock_session_id = f"cs_test_demo_{uuid.uuid4().hex[:16]}"
        checkout_url = f"{base_url}/checkout/sandbox-simulator/?session_id={mock_session_id}&product_slug={product.slug}"
        if customer_email:
            checkout_url += f"&email={customer_email}"

        return {
            'session_id': mock_session_id,
            'url': checkout_url,
            'is_simulated': True
        }

    @classmethod
    def process_checkout_completed(cls, session_data: dict) -> Order:
        """
        Fulfills an order from a verified Stripe checkout.session.completed event or simulator.
        Guarantees idempotency by checking existing session IDs.
        """
        session_id = session_data.get('id', '')
        
        # Check if already processed
        existing_order = Order.objects.filter(stripe_checkout_session_id=session_id).first()
        if existing_order and existing_order.payment_status == 'paid':
            logger.info(f"Order for session {session_id} already fulfilled. Skipping.")
            return existing_order

        # Extract customer details
        customer_details = session_data.get('customer_details') or {}
        customer_email = customer_details.get('email') or session_data.get('customer_email') or 'student@example.com'
        customer_name = customer_details.get('name') or customer_email.split('@')[0].capitalize()
        stripe_customer_id = session_data.get('customer') or ''
        payment_intent_id = session_data.get('payment_intent') or f"pi_{session_id[-10:]}"
        
        amount_total = Decimal(session_data.get('amount_total', 0)) / Decimal('100.00')
        currency = session_data.get('currency', 'usd').upper()

        # Find or create customer
        customer, _ = Customer.objects.get_or_create(
            email__iexact=customer_email,
            defaults={
                'email': customer_email,
                'name': customer_name,
                'stripe_customer_id': stripe_customer_id,
            }
        )
        if not customer.name and customer_name:
            customer.name = customer_name
            customer.save(update_fields=['name'])

        # Find product from metadata
        metadata = session_data.get('metadata') or {}
        product_slug = metadata.get('product_slug')
        product_id = metadata.get('product_id')

        product = None
        if product_slug:
            product = Product.objects.filter(slug=product_slug).first()
        elif product_id:
            product = Product.objects.filter(id=product_id).first()

        if not product and amount_total > 0:
            product = Product.objects.filter(price=amount_total).first()
        if not product:
            product = Product.objects.first()

        # Create or update Order
        if existing_order:
            order = existing_order
            order.status = 'completed'
            order.payment_status = 'paid'
            order.stripe_payment_intent_id = payment_intent_id
            order.total = amount_total or (product.price if product else Decimal('19.00'))
            order.save()
        else:
            order = Order.objects.create(
                customer=customer,
                customer_name=customer_name,
                customer_email=customer_email,
                status='completed',
                payment_status='paid',
                total=amount_total if amount_total > 0 else (product.price if product else Decimal('19.00')),
                currency=currency,
                stripe_checkout_session_id=session_id,
                stripe_payment_intent_id=payment_intent_id,
            )

        # Create OrderItem if not exists
        if not order.items.exists() and product:
            OrderItem.objects.create(
                order=order,
                product=product,
                product_title=product.title,
                price=product.price,
                quantity=1
            )

        # Record Payment record
        Payment.objects.get_or_create(
            order=order,
            provider_reference=payment_intent_id,
            defaults={
                'provider': 'stripe',
                'status': 'succeeded',
                'amount': order.total,
                'currency': order.currency,
                'metadata': session_data,
            }
        )

        # Recalculate customer statistics
        customer.recalculate_stats()

        # Dispatch purchase confirmation email
        send_purchase_confirmation(order)

        return order

    @classmethod
    def verify_and_process_webhook(cls, payload_body: bytes, sig_header: str) -> tuple[bool, str]:
        """
        Parses and verifies Stripe webhook HMAC signature, records the event,
        and dispatches to handler.
        """
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        event = None

        try:
            if webhook_secret and not webhook_secret.startswith('whsec_sample'):
                event = stripe.Webhook.construct_event(
                    payload=payload_body,
                    sig_header=sig_header,
                    secret=webhook_secret
                )
            else:
                # In test/dev mode without signing secret configured
                event_data = json.loads(payload_body.decode('utf-8'))
                event = event_data
        except Exception as e:
            logger.error(f"Webhook signature or parse error: {e}")
            return False, f"Signature verification failed: {str(e)}"

        event_id = event.get('id', f"evt_manual_{timezone.now().timestamp()}")
        event_type = event.get('type', 'unknown')

        # Idempotency check on WebhookEvent
        webhook_record, created = WebhookEvent.objects.get_or_create(
            event_id=event_id,
            defaults={
                'event_type': event_type,
                'payload': event if isinstance(event, dict) else event.to_dict_recursive(),
            }
        )

        if not created and webhook_record.processed:
            logger.info(f"Webhook event {event_id} already processed.")
            return True, "Already processed"

        try:
            if event_type == 'checkout.session.completed':
                session_obj = event.get('data', {}).get('object', {})
                cls.process_checkout_completed(session_obj)

            webhook_record.processed = True
            webhook_record.save(update_fields=['processed'])
            return True, "Event handled successfully"
        except Exception as e:
            logger.error(f"Error handling webhook {event_id}: {e}")
            webhook_record.error_message = str(e)
            webhook_record.save(update_fields=['error_message'])
            return False, str(e)
