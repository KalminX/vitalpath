from django.db import models
from django.utils.text import slugify
from django.utils import timezone

class YouTubeVideo(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    video_id = models.CharField(max_length=100, help_text="YouTube Video ID (e.g. dQw4w9WgXcQ) or embed URL")
    thumbnail_url = models.CharField(max_length=500, blank=True, help_text="Custom thumbnail image URL or auto-generated from YouTube")
    duration = models.CharField(max_length=30, default="12:45", help_text="Duration string e.g. 14:30")
    category = models.CharField(max_length=100, default="Health Principles")
    featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    published_at = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['order', '-published_at']
        verbose_name = 'YouTube Video'
        verbose_name_plural = 'YouTube Videos'

    def __str__(self):
        return f"{self.title} ({self.duration})"

    @property
    def computed_thumbnail(self):
        if self.thumbnail_url:
            return self.thumbnail_url
        if self.video_id and not self.video_id.startswith('http'):
            return f"https://img.youtube.com/vi/{self.video_id}/hqdefault.jpg"
        return "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=800&auto=format&fit=crop&q=80"

    @property
    def watch_url(self):
        if self.video_id.startswith('http'):
            return self.video_id
        return f"https://www.youtube.com/watch?v={self.video_id}"


class EducationalResource(models.Model):
    RESOURCE_TYPES = [
        ('guide', 'Illustrated Guide'),
        ('checklist', 'Action Checklist'),
        ('reference', 'Reference Chart'),
        ('worksheet', 'Self-Assessment Worksheet'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    summary = models.TextField()
    resource_type = models.CharField(max_length=30, choices=RESOURCE_TYPES, default='guide')
    read_time = models.CharField(max_length=30, default='5 min read')
    format_label = models.CharField(max_length=50, default='PDF + Interactive')
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    published_at = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['order', '-published_at']
        verbose_name = 'Educational Resource'
        verbose_name_plural = 'Educational Resources'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
