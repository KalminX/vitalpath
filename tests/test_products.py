from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from apps.products.models import Product, Category, ProductModule

class ProductTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Foundations", slug="foundations")
        self.product_published = Product.objects.create(
            title="Health Education Fundamentals",
            slug="health-education-fundamentals",
            category=self.category,
            short_description="Core physiological basics.",
            description="Detailed curriculum overview.",
            price=Decimal("19.00"),
            status="published",
            featured=True,
            what_is_included="Module 1\nModule 2\nPDF Guide",
            who_it_is_for="Curious learners\nBusy adults",
            target_outcomes="Understand sleep\nUnderstand nutrition",
        )
        self.module1 = ProductModule.objects.create(
            product=self.product_published,
            title="Module 1: The Human Operating System",
            duration="20 mins",
            order=0
        )
        self.product_draft = Product.objects.create(
            title="Advanced Circadian Biology (Draft)",
            slug="advanced-circadian-biology",
            price=Decimal("49.00"),
            status="draft",
            featured=False
        )

    def test_product_model_properties(self):
        self.assertTrue(self.product_published.is_published)
        self.assertFalse(self.product_draft.is_published)
        self.assertEqual(self.product_published.price_in_cents, 1900)
        self.assertEqual(len(self.product_published.included_items_list), 3)
        self.assertEqual(len(self.product_published.who_it_is_for_list), 2)
        self.assertEqual(len(self.product_published.outcomes_list), 2)

    def test_catalog_view_only_shows_published(self):
        response = self.client.get(reverse('products:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Health Education Fundamentals")
        self.assertNotContains(response, "Advanced Circadian Biology (Draft)")

    def test_catalog_category_filter(self):
        response = self.client.get(f"{reverse('products:list')}?category=foundations")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Health Education Fundamentals")

    def test_product_detail_view(self):
        response = self.client.get(reverse('products:detail', kwargs={'slug': self.product_published.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Health Education Fundamentals")
        self.assertContains(response, "Module 1: The Human Operating System")
        self.assertContains(response, "$19.00")

    def test_draft_product_detail_returns_404(self):
        response = self.client.get(reverse('products:detail', kwargs={'slug': self.product_draft.slug}))
        self.assertEqual(response.status_code, 404)
