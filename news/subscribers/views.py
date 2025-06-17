from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.http import Http404
from django.utils import timezone
from .models import Subscriber
from .forms import SubscriptionForm, UnsubscribeForm
# Removed Celery task imports - using direct email sending


def subscribe(request):
    """Handle newsletter subscription"""
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            # Check if subscriber already exists
            try:
                subscriber = Subscriber.objects.get(email=email)
                created = False
                # If subscriber exists but is inactive or unconfirmed, reactivate them
                if not subscriber.is_active or not subscriber.is_confirmed:
                    subscriber.first_name = form.cleaned_data.get('first_name', subscriber.first_name)
                    subscriber.last_name = form.cleaned_data.get('last_name', subscriber.last_name)
                    subscriber.is_active = True
                    subscriber.is_confirmed = True
                    subscriber.date_confirmed = timezone.now()
                    subscriber.date_unsubscribed = None
                    subscriber.date_subscribed = timezone.now()  # Update subscription date
                    subscriber.save()
                    created = True  # Treat as new subscription for welcome email
                    print(f"✅ Reactivated subscriber: {subscriber.email}")
            except Subscriber.DoesNotExist:
                subscriber = Subscriber.objects.create(
                    email=email,
                    first_name=form.cleaned_data.get('first_name', ''),
                    last_name=form.cleaned_data.get('last_name', ''),
                )
                created = True
                print(f"✅ Created new subscriber: {subscriber.email}")

            # Check if confirmation is required
            from django.conf import settings
            require_confirmation = getattr(settings, 'NEWSLETTER_REQUIRE_CONFIRMATION', False)

            if created or not subscriber.is_confirmed:
                if not require_confirmation:
                    # Auto-confirm immediately - no email confirmation needed
                    subscriber.confirm_subscription()
                    messages.success(
                        request,
                        'Welcome! You have been successfully subscribed to our newsletter. Check your email for a welcome message!'
                    )
                    return redirect('subscribers:subscription_success')
                # Send confirmation email (try Celery first, fallback to direct send)
                try:
                    send_confirmation_email_task.delay(subscriber.id)
                except Exception as e:
                    # Fallback to direct email sending if Celery is not available
                    from django.core.mail import send_mail
                    from django.template.loader import render_to_string
                    from django.conf import settings

                    confirmation_url = f"{settings.SITE_URL}/confirm/{subscriber.confirmation_token}/"

                    context = {
                        'subscriber': subscriber,
                        'confirmation_url': confirmation_url,
                    }

                    html_content = render_to_string('subscribers/email/confirmation.html', context)

                    try:
                        send_mail(
                            subject='Confirm your newsletter subscription',
                            message=f'Please confirm your subscription by visiting: {confirmation_url}',
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[subscriber.email],
                            html_message=html_content,
                            fail_silently=False,
                        )
                    except Exception as email_error:
                        print(f"Email sending failed: {email_error}")
                        # For development, we'll just print the confirmation URL
                        print(f"CONFIRMATION URL: {confirmation_url}")

                messages.success(
                    request,
                    'Thank you for subscribing! Please check your email to confirm your subscription.'
                )
            else:
                messages.info(request, 'You are already subscribed to our newsletter.')

            return redirect('subscribers:subscription_success')
    else:
        form = SubscriptionForm()

    return render(request, 'subscribers/subscribe.html', {'form': form})


def subscription_success(request):
    """Display subscription success page"""
    return render(request, 'subscribers/subscription_success.html')


def confirm_subscription(request, token):
    """Confirm newsletter subscription"""
    try:
        subscriber = Subscriber.objects.get(confirmation_token=token)

        if subscriber.is_confirmed:
            messages.info(request, 'Your subscription is already confirmed.')
        elif subscriber.is_confirmation_expired():
            messages.error(request, 'Your confirmation link has expired. Please subscribe again.')
            return redirect('subscribers:subscribe')
        else:
            subscriber.confirm_subscription()
            messages.success(request, 'Thank you! Your subscription has been confirmed.')

        return render(request, 'subscribers/confirmation_success.html', {'subscriber': subscriber})

    except Subscriber.DoesNotExist:
        messages.error(request, 'Invalid confirmation link.')
        return redirect('subscribers:subscribe')


def unsubscribe_form(request):
    """Display unsubscribe form"""
    if request.method == 'POST':
        form = UnsubscribeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                subscriber = Subscriber.objects.get(email=email, is_active=True)
                subscriber.unsubscribe()
                messages.success(request, 'You have been successfully unsubscribed.')
                return redirect('subscribers:unsubscribe_success')
            except Subscriber.DoesNotExist:
                messages.error(request, 'Email not found in our subscription list.')
    else:
        form = UnsubscribeForm()

    return render(request, 'subscribers/unsubscribe.html', {'form': form})


def unsubscribe_direct(request, token):
    """Direct unsubscribe via token (from email link)"""
    try:
        subscriber = Subscriber.objects.get(confirmation_token=token, is_active=True)
        subscriber.unsubscribe()
        messages.success(request, 'You have been successfully unsubscribed.')
        return render(request, 'subscribers/unsubscribe_success.html', {'subscriber': subscriber})
    except Subscriber.DoesNotExist:
        messages.error(request, 'Invalid unsubscribe link.')
        return redirect('subscribers:subscribe')


def unsubscribe_success(request):
    """Display unsubscribe success page"""
    return render(request, 'subscribers/unsubscribe_success.html')
