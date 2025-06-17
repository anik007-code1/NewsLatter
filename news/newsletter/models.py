from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


class Newsletter(models.Model):
    """Model for newsletter campaigns"""
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=200, help_text="Email subject line")
    content = models.TextField(help_text="Newsletter content (HTML allowed)")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    scheduled_date = models.DateTimeField(null=True, blank=True)

    # Status
    is_sent = models.BooleanField(default=False)
    sent_date = models.DateTimeField(null=True, blank=True)

    # Statistics
    total_recipients = models.PositiveIntegerField(default=0)
    total_sent = models.PositiveIntegerField(default=0)
    total_failed = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Newsletter'
        verbose_name_plural = 'Newsletters'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('newsletter:detail', kwargs={'pk': self.pk})

    @property
    def status(self):
        if self.is_sent:
            return 'Sent'
        elif self.is_scheduled and self.scheduled_date:
            if self.scheduled_date > timezone.now():
                return 'Scheduled'
            else:
                return 'Ready to Send'
        else:
            return 'Draft'


class NewsletterSendLog(models.Model):
    """Log of newsletter sends to track delivery"""
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, related_name='send_logs')
    recipient_email = models.EmailField()
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
    ], default='sent')
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-sent_at']
        unique_together = ['newsletter', 'recipient_email']

    def __str__(self):
        return f"{self.newsletter.title} -> {self.recipient_email}"
