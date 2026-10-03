from decimal import Decimal
from django.test import TestCase, override_settings
from django.core import mail
from apps.products.models import Product
from apps.orders.models import Customer, Order, OrderItem
from apps.core.models import WaitlistLead, ContactMessage
from apps.notifications.services import send_purchase_confirmation, send_waitlist_confirmation, send_contact_notification

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class NotificationTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            title="Health Education Fundamentals",
            slug="health-education-fundamentals",
            price=Decimal("19.00"),
            status="published"
        )
        self.customer = Customer.objects.create(
            email="buyer@example.com",
            name="Alex Buyer"
        )
        self.order = Order.objects.create(
            customer=self.customer,
            customer_name=self.customer.name,
            customer_email=self.customer.email,
            status="completed",
            payment_status="paid",
            total=Decimal("19.00")
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_title=self.product.title,
            price=self.product.price,
            quantity=1
        )

    def test_send_purchase_confirmation_email(self):
        mail.outbox = []
        result = send_purchase_confirmation(self.order)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ["buyer@example.com"])
        self.assertIn(self.order.order_number, email.subject)
        self.assertIn("Health Education Fundamentals", email.body)

    def test_send_waitlist_confirmation_email(self):
        mail.outbox = []
        lead = WaitlistLead.objects.create(
            email="interested@example.com",
            name="Sam Interested",
            interest_area="telegram"
        )
        result = send_waitlist_confirmation(lead)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["interested@example.com"])

    def test_send_contact_notification(self):
        mail.outbox = []
        msg = ContactMessage.objects.create(
            name="Inquiry Person",
            email="inquiry@example.com",
            subject="Question regarding course access",
            message="Can I access the courses from an iPad?"
        )
        result = send_contact_notification(msg)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Inquiry Person", mail.outbox[0].subject)
