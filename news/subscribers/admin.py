from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Subscriber


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'full_name', 'is_active', 'is_confirmed', 'date_subscribed', 'confirmation_status']
    list_filter = ['is_active', 'is_confirmed', 'date_subscribed', 'date_confirmed']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['confirmation_token', 'date_subscribed', 'date_confirmed', 'date_unsubscribed']

    fieldsets = (
        ('Personal Information', {
            'fields': ('email', 'first_name', 'last_name')
        }),
        ('Subscription Status', {
            'fields': ('is_active', 'is_confirmed')
        }),
        ('Dates', {
            'fields': ('date_subscribed', 'date_confirmed', 'date_unsubscribed'),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('confirmation_token',),
            'classes': ('collapse',)
        }),
    )

    actions = ['activate_subscribers', 'deactivate_subscribers', 'confirm_subscribers']

    def confirmation_status(self, obj):
        if obj.is_confirmed:
            return format_html('<span style="color: green;">✓ Active Subscriber</span>')
        else:
            return format_html('<span style="color: orange;">⏳ Inactive</span>')
    confirmation_status.short_description = 'Status'

    def activate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} subscribers activated.')
    activate_subscribers.short_description = 'Activate selected subscribers'

    def deactivate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} subscribers deactivated.')
    deactivate_subscribers.short_description = 'Deactivate selected subscribers'

    def confirm_subscribers(self, request, queryset):
        updated = 0
        for subscriber in queryset:
            if not subscriber.is_confirmed:
                subscriber.confirm_subscription()
                updated += 1
        self.message_user(request, f'{updated} subscribers confirmed.')
    confirm_subscribers.short_description = 'Confirm selected subscribers'
