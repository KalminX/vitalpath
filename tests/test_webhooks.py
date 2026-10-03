import json
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from apps.products.models import Product
from apps.orders.models import Order, Customer, WebhookEvent

class WebhookTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(
            title="Building Better Health Habits",
            slug="building-better-health-habits",
            price=Decimal("24.00"),
            status="published"
        )

    def test_webhook_checkout_session_completed(self):
        payload = {
            'id': 'evt_test_checkout_001',
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_test_webhook_session_111',
                    'customer_details': {
                        'email': 'webhook.student@example.com',
                        'name': 'Webhook Student',
                    },
                    'amount_total': 2400,
                    'currency': 'usd',
                    'payment_intent': 'pi_webhook_test_222',
                    'metadata': {
                        'product_slug': self.product.slug,
                    }
                }
            }
        }

        response = self.client.post(
            reverse('orders:stripe_webhook'),
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        
        # Webhook event record verification
        evt_record = WebhookEvent.objects.get(event_id='evt_test_checkout_001')
        self.assertTrue(evt_record.processed)

        # Order creation verification
        order = Order.objects.get(stripe_checkout_session_id='cs_test_webhook_session_111')
        self.assertEqual(order.payment_status, 'paid')
        self.assertEqual(order.customer_email, 'webhook.student@example.com')
        self.assertEqual(order.total, Decimal('24.00'))

    def test_webhook_idempotency_duplicate_event(self):
        payload = {
            'id': 'evt_duplicate_test',
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_test_dup_123',
                    'customer_details': {'email': 'dup@example.com', 'name': 'Dup Student'},
                    'amount_total': 2400,
                    'metadata': {'product_slug': self.product.slug}
                }
            }
        }

        # First post
        res1 = self.client.post(reverse('orders:stripe_webhook'), data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res1.status_code, 200)

        # Second post
        res2 = self.client.post(reverse('orders:stripe_webhook'), data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res2.status_code, 200)

        # Should only have 1 order
        self.assertEqual(Order.objects.filter(stripe_checkout_session_id='cs_test_dup_123').count(), 1)
