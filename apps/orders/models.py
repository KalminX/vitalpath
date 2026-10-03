import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone
from apps.products.models import Product

class Customer(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('vip', 'VIP / Repeat Buyer'),
        ('inactive', 'Inactive'),
    ]

    email = models.EmailField(unique=True, db_index=True)
    name = models.CharField(max_length=150, blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True, db_index=True)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    orders_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True, help_text="Creator internal notes about this customer")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        return f"{self.name or self.email} ({self.email})"

    def recalculate_stats(self):
        """Updates total_spent, orders_count, and status based on completed orders."""
        completed_orders = self.orders.filter(status='completed', payment_status='paid')
        self.orders_count = completed_orders.count()
        total = sum(order.total for order in completed_orders) or Decimal('0.00')
        self.total_spent = total
        if self.orders_count >= 3 or self.total_spent >= Decimal('100.00'):
            self.status = 'vip'
        elif self.orders_count >= 1:
            self.status = 'active'
        self.save(update_fields=['orders_count', 'total_spent', 'status', 'updated_at'])

    @property
    def last_purchase_date(self):
        last_order = self.orders.filter(payment_status='paid').order_by('-created_at').first()
        return last_order.created_at if last_order else None


def generate_order_number():
    """Generates human-readable unique order number e.g. VP-98421"""
    return f"VP-{uuid.uuid4().hex[:6].upper()}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pending', 'Pending Payment'),
        ('failed', 'Payment Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
        ('refunded', 'Refunded'),
    ]

    order_number = models.CharField(max_length=32, unique=True, default=generate_order_number, db_index=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    customer_name = models.CharField(max_length=150, blank=True)
    customer_email = models.EmailField(db_index=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=3, default='USD')
    
    stripe_checkout_session_id = models.CharField(max_length=200, blank=True, db_index=True)
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True, db_index=True)
    
    email_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        indexes = [
            models.Index(fields=['status', 'payment_status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Order {self.order_number} - ${self.total} ({self.customer_email})"

    @property
    def is_paid(self):
        return self.payment_status == 'paid'

    @property
    def primary_product(self):
        first_item = self.items.first()
        return first_item.product if first_item else None

    @property
    def primary_product_title(self):
        first_item = self.items.first()
        if first_item:
            return first_item.product_title
        return "Educational Digital Access"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    product_title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f"{self.quantity}x {self.product_title} (${self.price})"

    @property
    def subtotal(self):
        return self.price * self.quantity


class Payment(models.Model):
    STATUS_CHOICES = [
        ('succeeded', 'Succeeded'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    provider = models.CharField(max_length=50, default='stripe')
    provider_reference = models.CharField(max_length=200, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='succeeded')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment Record'
        verbose_name_plural = 'Payment Records'

    def __str__(self):
        return f"{self.provider.upper()} {self.provider_reference} - ${self.amount} ({self.status})"


class WebhookEvent(models.Model):
    event_id = models.CharField(max_length=200, unique=True, db_index=True)
    event_type = models.CharField(max_length=100)
    processed = models.BooleanField(default=False)
    payload = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Stripe Webhook Event'
        verbose_name_plural = 'Stripe Webhook Events'

    def __str__(self):
        return f"{self.event_type} [{self.event_id}] - {'Processed' if self.processed else 'Pending/Failed'}"
