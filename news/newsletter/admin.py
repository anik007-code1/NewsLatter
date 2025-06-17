from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Newsletter, NewsletterSendLog


class NewsletterSendLogInline(admin.TabularInline):
    model = NewsletterSendLog
    extra = 0
    readonly_fields = ['recipient_email', 'sent_at', 'status', 'error_message']
    can_delete = False


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'status_display', 'created_by', 'created_at', 'scheduled_date', 'total_recipients']
    list_filter = ['is_sent', 'is_scheduled', 'created_at', 'sent_date']
    search_fields = ['title', 'subject', 'content']
    readonly_fields = ['created_at', 'updated_at', 'sent_date', 'total_recipients', 'total_sent', 'total_failed']

    fieldsets = (
        ('Newsletter Content', {
            'fields': ('title', 'subject', 'content')
        }),
        ('Scheduling', {
            'fields': ('is_scheduled', 'scheduled_date')
        }),
        ('Status', {
            'fields': ('is_sent', 'sent_date'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('total_recipients', 'total_sent', 'total_failed'),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [NewsletterSendLogInline]
    actions = ['send_newsletter', 'schedule_newsletter']

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new newsletter
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def status_display(self, obj):
        status = obj.status
        if status == 'Sent':
            return format_html('<span style="color: green;">✓ {}</span>', status)
        elif status == 'Scheduled':
            return format_html('<span style="color: blue;">📅 {}</span>', status)
        elif status == 'Ready to Send':
            return format_html('<span style="color: orange;">⚡ {}</span>', status)
        else:
            return format_html('<span style="color: gray;">📝 {}</span>', status)
    status_display.short_description = 'Status'

    def send_newsletter(self, request, queryset):
        from .tasks import send_newsletter_direct
        count = 0
        for newsletter in queryset:
            if not newsletter.is_sent:
                send_newsletter_direct(newsletter.id)
                count += 1
        self.message_user(request, f'{count} newsletters sent successfully.')
    send_newsletter.short_description = 'Send selected newsletters'

    def schedule_newsletter(self, request, queryset):
        updated = queryset.update(is_scheduled=True, scheduled_date=timezone.now())
        self.message_user(request, f'{updated} newsletters scheduled.')
    schedule_newsletter.short_description = 'Schedule selected newsletters'


@admin.register(NewsletterSendLog)
class NewsletterSendLogAdmin(admin.ModelAdmin):
    list_display = ['newsletter', 'recipient_email', 'status', 'sent_at']
    list_filter = ['status', 'sent_at']
    search_fields = ['newsletter__title', 'recipient_email']
    readonly_fields = ['newsletter', 'recipient_email', 'sent_at', 'status', 'error_message']
