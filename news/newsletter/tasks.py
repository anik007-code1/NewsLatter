# Celery removed - using direct email sending functions instead
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from .models import Newsletter, NewsletterSendLog
from subscribers.models import Subscriber
import logging

logger = logging.getLogger(__name__)


def send_newsletter_direct(newsletter_id):
    """
    Send newsletter to all active subscribers (direct email sending)
    """
    try:
        newsletter = Newsletter.objects.get(id=newsletter_id)
        
        if newsletter.is_sent:
            logger.warning(f"Newsletter {newsletter_id} already sent")
            return f"Newsletter {newsletter.title} already sent"
        
        # Get all active subscribers
        subscribers = Subscriber.objects.filter(is_active=True, is_confirmed=True)
        
        newsletter.total_recipients = subscribers.count()
        newsletter.save()
        
        sent_count = 0
        failed_count = 0
        
        for subscriber in subscribers:
            try:
                # Send individual email
                success = send_newsletter_email(newsletter, subscriber)
                if success:
                    sent_count += 1
                    # Log successful send
                    NewsletterSendLog.objects.create(
                        newsletter=newsletter,
                        recipient_email=subscriber.email,
                        status='sent'
                    )
                else:
                    failed_count += 1
                    # Log failed send
                    NewsletterSendLog.objects.create(
                        newsletter=newsletter,
                        recipient_email=subscriber.email,
                        status='failed',
                        error_message='Failed to send email'
                    )
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to send newsletter to {subscriber.email}: {str(e)}")
                # Log failed send with error
                NewsletterSendLog.objects.create(
                    newsletter=newsletter,
                    recipient_email=subscriber.email,
                    status='failed',
                    error_message=str(e)
                )
        
        # Update newsletter status
        newsletter.total_sent = sent_count
        newsletter.total_failed = failed_count
        newsletter.is_sent = True
        newsletter.sent_date = timezone.now()
        newsletter.save()
        
        logger.info(f"Newsletter {newsletter.title} sent to {sent_count} subscribers, {failed_count} failed")
        return f"Newsletter sent to {sent_count} subscribers, {failed_count} failed"
        
    except Newsletter.DoesNotExist:
        logger.error(f"Newsletter {newsletter_id} not found")
        return f"Newsletter {newsletter_id} not found"
    except Exception as e:
        logger.error(f"Error sending newsletter {newsletter_id}: {str(e)}")
        return f"Error sending newsletter: {str(e)}"


def send_newsletter_email(newsletter, subscriber):
    """
    Send newsletter email to a single subscriber
    """
    try:
        # Create unsubscribe URL
        unsubscribe_url = f"{settings.SITE_URL}/unsubscribe/{subscriber.confirmation_token}/"
        
        # Prepare email context
        context = {
            'newsletter': newsletter,
            'subscriber': subscriber,
            'unsubscribe_url': unsubscribe_url,
        }
        
        # Render email content
        html_content = render_to_string('newsletter/email/newsletter.html', context)
        text_content = strip_tags(html_content)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=newsletter.subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[subscriber.email]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {subscriber.email}: {str(e)}")
        return False


def send_confirmation_email_direct(subscriber_id):
    """
    Send confirmation email to new subscriber (direct sending)
    """
    try:
        subscriber = Subscriber.objects.get(id=subscriber_id)
        
        # Create confirmation URL
        confirmation_url = f"{settings.SITE_URL}/confirm/{subscriber.confirmation_token}/"
        
        # Prepare email context
        context = {
            'subscriber': subscriber,
            'confirmation_url': confirmation_url,
        }
        
        # Render email content
        html_content = render_to_string('subscribers/email/confirmation.html', context)
        text_content = strip_tags(html_content)
        
        # Send confirmation email
        email = EmailMultiAlternatives(
            subject='Confirm your newsletter subscription',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[subscriber.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f"Confirmation email sent to {subscriber.email}")
        return f"Confirmation email sent to {subscriber.email}"
        
    except Subscriber.DoesNotExist:
        logger.error(f"Subscriber {subscriber_id} not found")
        return f"Subscriber {subscriber_id} not found"
    except Exception as e:
        logger.error(f"Error sending confirmation email to subscriber {subscriber_id}: {str(e)}")
        return f"Error sending confirmation email: {str(e)}"


def send_welcome_email_direct(subscriber_id):
    """
    Send welcome email to newly confirmed subscriber (direct sending)
    """
    try:
        subscriber = Subscriber.objects.get(id=subscriber_id)

        # Prepare email context
        context = {
            'subscriber': subscriber,
            'site_url': settings.SITE_URL,
        }

        # Render email content
        html_content = render_to_string('subscribers/email/welcome.html', context)
        text_content = strip_tags(html_content)

        # Send welcome email
        email = EmailMultiAlternatives(
            subject='Welcome to our Newsletter!',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[subscriber.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        logger.info(f"Welcome email sent to {subscriber.email}")
        return f"Welcome email sent to {subscriber.email}"

    except Subscriber.DoesNotExist:
        logger.error(f"Subscriber {subscriber_id} not found")
        return f"Subscriber {subscriber_id} not found"
    except Exception as e:
        logger.error(f"Error sending welcome email to subscriber {subscriber_id}: {str(e)}")
        return f"Error sending welcome email: {str(e)}"


def send_preview_email_direct(newsletter_id, preview_email):
    """
    Send preview email to specified email address (direct sending)
    """
    try:
        newsletter = Newsletter.objects.get(id=newsletter_id)
        
        # Prepare email context
        context = {
            'newsletter': newsletter,
            'is_preview': True,
        }
        
        # Render email content
        html_content = render_to_string('newsletter/email/newsletter.html', context)
        text_content = strip_tags(html_content)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=f"[PREVIEW] {newsletter.subject}",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[preview_email]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        
        logger.info(f"Preview email sent to {preview_email}")
        return f"Preview email sent to {preview_email}"
        
    except Newsletter.DoesNotExist:
        logger.error(f"Newsletter {newsletter_id} not found")
        return f"Newsletter {newsletter_id} not found"
    except Exception as e:
        logger.error(f"Error sending preview email: {str(e)}")
        return f"Error sending preview email: {str(e)}"
