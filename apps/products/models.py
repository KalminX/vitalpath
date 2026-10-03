from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    short_description = models.CharField(max_length=300)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('19.00'))
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    featured = models.BooleanField(default=False)
    
    format_type = models.CharField(max_length=100, default='Digital Guide & Curriculum')
    estimated_duration = models.CharField(max_length=50, default='Self-paced (approx. 3-4 hours)')
    level = models.CharField(max_length=50, default='All Levels / Practical Foundation')
    
    # Structured editorial text fields
    what_is_included = models.TextField(
        help_text="One item per line (e.g. 8 structured video modules, 45-page downloadable PDF guide, Practical habit checklist)",
        default="8 comprehensive educational modules\n45-page digital companion guide\nActionable daily implementation checklists\nLifetime access & future module updates"
    )
    who_it_is_for = models.TextField(
        help_text="One item per line",
        default="Individuals seeking clear, evidence-informed health principles\nBusy professionals wanting practical habits without extreme diets\nAnyone overwhelmed by conflicting online health advice"
    )
    target_outcomes = models.TextField(
        help_text="One item per line",
        default="Understand the core physiological basics of everyday wellbeing\nDevelop a sustainable, non-restrictive daily routine\nConfidently evaluate health claims and media headlines"
    )
    
    cover_image_url = models.CharField(
        max_length=500, 
        blank=True,
        help_text="URL for product cover visual"
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-featured', '-created_at']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        indexes = [
            models.Index(fields=['status', 'featured']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return f"{self.title} (${self.price})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def is_published(self):
        return self.status == 'published'

    @property
    def price_in_cents(self):
        return int(self.price * 100)

    @property
    def included_items_list(self):
        if not self.what_is_included:
            return []
        return [line.strip() for line in self.what_is_included.strip().splitlines() if line.strip()]

    @property
    def who_it_is_for_list(self):
        if not self.who_it_is_for:
            return []
        return [line.strip() for line in self.who_it_is_for.strip().splitlines() if line.strip()]

    @property
    def outcomes_list(self):
        if not self.target_outcomes:
            return []
        return [line.strip() for line in self.target_outcomes.strip().splitlines() if line.strip()]


class ProductModule(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration = models.CharField(max_length=50, blank=True, default='25 mins')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Product Module'
        verbose_name_plural = 'Product Modules'

    def __str__(self):
        return f"{self.product.title} - Module {self.order + 1}: {self.title}"


class ProductResource(models.Model):
    RESOURCE_TYPES = [
        ('pdf', 'PDF Guide & Workbook'),
        ('checklist', 'Action Checklist'),
        ('template', 'Planning Template'),
        ('audio', 'Audio Walkthrough'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, default='pdf')
    file_size = models.CharField(max_length=30, blank=True, default='2.4 MB PDF')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Product Resource'
        verbose_name_plural = 'Product Resources'

    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"


class ProductFAQ(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=250)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Product FAQ'
        verbose_name_plural = 'Product FAQs'

    def __str__(self):
        return self.question
