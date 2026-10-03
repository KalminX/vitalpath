from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from apps.products.models import Product
from apps.orders.models import Customer, Order, OrderItem, Payment
from apps.orders.services import StripeCheckoutService

class CheckoutAndOrderTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(
            title="Understanding Everyday Nutrition",
            slug="understanding-everyday-nutrition",
            short_description="Nutrition principles plainly explained.",
            description="Complete guide.",
            price=Decimal("29.00"),
            status="published"
        )

    def test_checkout_initiate_redirects(self):
        response = self.client.post(
            reverse('orders:checkout_initiate', kwargs={'slug': self.product.slug}),
            {'email': 'testbuyer@example.com'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue('checkout' in response.url)

    def test_checkout_fulfillment_service(self):
        session_data = {
            'id': 'cs_test_unique_12345',
            'customer_details': {
                'email': 'jane.doe@example.com',
                'name': 'Jane Doe',
            },
            'amount_total': 2900,
            'currency': 'usd',
            'payment_intent': 'pi_test_987654321',
            'customer': 'cus_test_111',
            'metadata': {
                'product_slug': self.product.slug,
                'product_id': str(self.product.id),
            }
        }

        order = StripeCheckoutService.process_checkout_completed(session_data)

        self.assertIsNotNone(order)
        self.assertEqual(order.payment_status, 'paid')
        self.assertEqual(order.status, 'completed')
        self.assertEqual(order.customer_email, 'jane.doe@example.com')
        self.assertEqual(order.total, Decimal('29.00'))

        # Customer record check
        customer = Customer.objects.get(email='jane.doe@example.com')
        self.assertEqual(customer.name, 'Jane Doe')
        self.assertEqual(customer.orders_count, 1)
        self.assertEqual(customer.total_spent, Decimal('29.00'))

        # Payment record check
        payment = Payment.objects.get(order=order)
        self.assertEqual(payment.provider_reference, 'pi_test_987654321')
        self.assertEqual(payment.status, 'succeeded')

        # Line item check
        item = order.items.first()
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.price, Decimal('29.00'))

    def test_checkout_idempotency(self):
        session_data = {
            'id': 'cs_test_idempotent_999',
            'customer_details': {'email': 'repeat@example.com', 'name': 'Repeat User'},
            'amount_total': 2900,
            'currency': 'usd',
            'metadata': {'product_slug': self.product.slug}
        }

        order1 = StripeCheckoutService.process_checkout_completed(session_data)
        order2 = StripeCheckoutService.process_checkout_completed(session_data)

        self.assertEqual(order1.id, order2.id)
        self.assertEqual(Order.objects.filter(stripe_checkout_session_id='cs_test_idempotent_999').count(), 1)
