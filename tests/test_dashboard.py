from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from apps.products.models import Product
from apps.orders.models import Customer, Order

class DashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Creator user (staff)
        self.creator = User.objects.create_user(
            username='creator@vitalpath.edu',
            email='creator@vitalpath.edu',
            password='TestPassword123!',
            is_staff=True
        )

        # Regular customer user (non-staff)
        self.regular_user = User.objects.create_user(
            username='student@example.com',
            email='student@example.com',
            password='TestPassword123!',
            is_staff=False
        )

        self.product = Product.objects.create(
            title="Health Education Fundamentals",
            slug="health-education-fundamentals",
            price=Decimal("19.00"),
            status="published"
        )

    def test_anonymous_user_redirected_from_dashboard(self):
        response = self.client.get(reverse('dashboard:overview'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue('login' in response.url)

    def test_non_staff_user_denied_access_to_dashboard(self):
        self.client.login(username='student@example.com', password='TestPassword123!')
        response = self.client.get(reverse('dashboard:overview'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url == '/')

    def test_creator_can_access_overview(self):
        self.client.login(username='creator@vitalpath.edu', password='TestPassword123!')
        response = self.client.get(reverse('dashboard:overview'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gross Revenue")
        self.assertContains(response, "Active Students")

    def test_creator_can_create_product(self):
        self.client.login(username='creator@vitalpath.edu', password='TestPassword123!')
        payload = {
            'title': 'New Circadian Masterguide',
            'slug': 'new-circadian-masterguide',
            'price': '35.00',
            'currency': 'USD',
            'status': 'published',
            'short_description': 'New masterguide short description.',
            'description': 'Full syllabus description.',
            'format_type': 'Digital Guide & Audio Modules',
            'estimated_duration': '2 hours',
            'level': 'Beginner',
            'what_is_included': '3 modules\n1 PDF',
            'who_it_is_for': 'Everyone',
            'target_outcomes': 'Better sleep',
        }
        response = self.client.post(reverse('dashboard:product_create'), payload)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(slug='new-circadian-masterguide').exists())

    def test_creator_toggle_product_status(self):
        self.client.login(username='creator@vitalpath.edu', password='TestPassword123!')
        self.assertEqual(self.product.status, 'published')
        
        response = self.client.post(reverse('dashboard:product_toggle_status', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, 302)
        
        self.product.refresh_from_db()
        self.assertEqual(self.product.status, 'draft')
