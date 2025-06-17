from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Newsletter
from .forms import NewsletterForm, NewsletterPreviewForm
from .tasks import send_newsletter_direct, send_preview_email_direct


def is_staff_user(user):
    """Check if user is staff"""
    return user.is_staff


def home(request):
    """Home page with subscription form"""
    from subscribers.forms import SubscriptionForm
    form = SubscriptionForm()
    return render(request, 'newsletter/home.html', {'form': form})


@login_required
@user_passes_test(is_staff_user)
def newsletter_list(request):
    """List all newsletters"""
    newsletters = Newsletter.objects.all()
    return render(request, 'newsletter/newsletter_list.html', {'newsletters': newsletters})


@login_required
@user_passes_test(is_staff_user)
def newsletter_detail(request, pk):
    """Display newsletter details"""
    newsletter = get_object_or_404(Newsletter, pk=pk)
    return render(request, 'newsletter/newsletter_detail.html', {'newsletter': newsletter})


@login_required
@user_passes_test(is_staff_user)
def newsletter_create(request):
    """Create new newsletter"""
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.created_by = request.user
            newsletter.save()

            # Handle different submit actions
            if 'save_and_send' in request.POST:
                send_newsletter_direct(newsletter.id)
                messages.success(request, 'Newsletter created and sent successfully!')
                return redirect('newsletter:detail', pk=newsletter.pk)
            elif 'save_and_preview' in request.POST:
                messages.success(request, 'Newsletter created successfully!')
                return redirect('newsletter:preview', pk=newsletter.pk)
            else:  # save_draft
                messages.success(request, 'Newsletter saved as draft!')
                return redirect('newsletter:detail', pk=newsletter.pk)
    else:
        form = NewsletterForm()

    return render(request, 'newsletter/newsletter_form.html', {'form': form, 'title': 'Create Newsletter'})


@login_required
@user_passes_test(is_staff_user)
def newsletter_edit(request, pk):
    """Edit existing newsletter"""
    newsletter = get_object_or_404(Newsletter, pk=pk)

    if newsletter.is_sent:
        messages.error(request, 'Cannot edit a newsletter that has already been sent.')
        return redirect('newsletter:detail', pk=newsletter.pk)

    if request.method == 'POST':
        form = NewsletterForm(request.POST, instance=newsletter)
        if form.is_valid():
            newsletter = form.save()

            # Handle different submit actions
            if 'save_and_send' in request.POST:
                send_newsletter_direct(newsletter.id)
                messages.success(request, 'Newsletter updated and sent successfully!')
                return redirect('newsletter:detail', pk=newsletter.pk)
            elif 'save_and_preview' in request.POST:
                messages.success(request, 'Newsletter updated successfully!')
                return redirect('newsletter:preview', pk=newsletter.pk)
            else:  # save_draft
                messages.success(request, 'Newsletter updated successfully!')
                return redirect('newsletter:detail', pk=newsletter.pk)
    else:
        form = NewsletterForm(instance=newsletter)

    return render(request, 'newsletter/newsletter_form.html', {
        'form': form,
        'newsletter': newsletter,
        'title': 'Edit Newsletter'
    })


@login_required
@user_passes_test(is_staff_user)
def newsletter_preview(request, pk):
    """Preview newsletter and send test email"""
    newsletter = get_object_or_404(Newsletter, pk=pk)

    if request.method == 'POST':
        form = NewsletterPreviewForm(request.POST)
        if form.is_valid():
            preview_email = form.cleaned_data['preview_email']
            send_preview_email_direct(newsletter.id, preview_email)
            messages.success(request, f'Preview email sent to {preview_email}')
            return redirect('newsletter:preview', pk=newsletter.pk)
    else:
        form = NewsletterPreviewForm()

    return render(request, 'newsletter/newsletter_preview.html', {
        'newsletter': newsletter,
        'form': form
    })


@login_required
@user_passes_test(is_staff_user)
@require_POST
def newsletter_send(request, pk):
    """Send newsletter to all subscribers"""
    newsletter = get_object_or_404(Newsletter, pk=pk)

    if newsletter.is_sent:
        messages.error(request, 'This newsletter has already been sent.')
    else:
        send_newsletter_direct(newsletter.id)
        messages.success(request, 'Newsletter sent successfully!')

    return redirect('newsletter:detail', pk=newsletter.pk)


@login_required
@user_passes_test(is_staff_user)
def newsletter_delete(request, pk):
    """Delete newsletter"""
    newsletter = get_object_or_404(Newsletter, pk=pk)

    if newsletter.is_sent:
        messages.error(request, 'Cannot delete a newsletter that has already been sent.')
        return redirect('newsletter:detail', pk=newsletter.pk)

    if request.method == 'POST':
        newsletter.delete()
        messages.success(request, 'Newsletter deleted successfully!')
        return redirect('newsletter:list')

    return render(request, 'newsletter/newsletter_confirm_delete.html', {'newsletter': newsletter})
