from django.db import models
from django.utils import timezone

class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.name} ({self.email}) - {self.subject or 'General Inquiry'}"


class WaitlistLead(models.Model):
    INTEREST_CHOICES = [
        ('all', 'All Upcoming Programs & Community'),
        ('telegram', 'Telegram Broadcasts & Live Q&A'),
        ('membership', 'Private Membership & Masterclasses'),
        ('nutrition', 'Everyday Nutrition Guides'),
        ('habits', 'Health Habit Systems'),
    ]

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150, blank=True)
    interest_area = models.CharField(max_length=50, choices=INTEREST_CHOICES, default='all')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Waitlist Lead'
        verbose_name_plural = 'Waitlist Leads'

    def __str__(self):
        return f"{self.email} - {self.get_interest_area_display()}"
