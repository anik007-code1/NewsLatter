import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings


class Subscriber(models.Model):
    """Model for newsletter subscribers"""
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    confirmation_token = models.UUIDField(default=uuid.uuid4, editable=False)
    date_subscribed = models.DateTimeField(auto_now_add=True)
    date_confirmed = models.DateTimeField(null=True, blank=True)
    date_unsubscribed = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date_subscribed']
        verbose_name = 'Subscriber'
        verbose_name_plural = 'Subscribers'

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def confirm_subscription(self):
        """Confirm the subscription and send welcome email"""
        was_confirmed = self.is_confirmed
        self.is_confirmed = True
        self.is_active = True
        self.date_confirmed = timezone.now()
        self.save()

        # Send welcome email only if this is the first confirmation
        if not was_confirmed:
            # Send welcome email directly (no Celery dependency)
            self._send_welcome_email_direct()

    def _send_welcome_email_direct(self):
        """Direct welcome email sending"""
        try:
            from django.core.mail import EmailMultiAlternatives
            from django.template.loader import render_to_string
            from django.utils.html import strip_tags
            from django.conf import settings

            print(f"📧 Sending welcome email to {self.email}...")

            context = {
                'subscriber': self,
                'site_url': settings.SITE_URL,
            }

            html_content = render_to_string('subscribers/email/welcome.html', context)
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject='🎉 Welcome to our Newsletter!',
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[self.email]
            )
            email.attach_alternative(html_content, "text/html")

            result = email.send()
            print(f"✅ Welcome email sent to {self.email}! Result: {result}")
            return True

        except Exception as e:
            print(f"❌ Failed to send welcome email to {self.email}: {str(e)}")
            return False

    def unsubscribe(self):
        """Unsubscribe the user"""
        self.is_active = False
        self.date_unsubscribed = timezone.now()
        self.save()

    def is_confirmation_expired(self):
        """Check if confirmation token is expired"""
        expiry_date = self.date_subscribed + timedelta(days=settings.NEWSLETTER_CONFIRMATION_DAYS)
        return timezone.now() > expiry_date
