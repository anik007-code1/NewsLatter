#!/usr/bin/env python
"""
Quick test script to verify forms are working
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsletter_project.settings')
django.setup()

from subscribers.forms import SubscriptionForm, UnsubscribeForm
from newsletter.forms import NewsletterForm

def test_subscription_form():
    """Test subscription form"""
    print("🧪 Testing Subscription Form...")
    
    # Test valid form
    form_data = {
        'email': 'newuser@example.com',
        'first_name': 'New',
        'last_name': 'User'
    }
    form = SubscriptionForm(data=form_data)
    
    if form.is_valid():
        print("✅ Subscription form validation passed")
        print(f"   Email: {form.cleaned_data['email']}")
        print(f"   Name: {form.cleaned_data['first_name']} {form.cleaned_data['last_name']}")
    else:
        print("❌ Subscription form validation failed")
        print(f"   Errors: {form.errors}")
    
    # Test form rendering
    form_html = str(form)
    if 'email' in form_html and 'first_name' in form_html:
        print("✅ Subscription form renders correctly")
    else:
        print("❌ Subscription form rendering issue")

def test_unsubscribe_form():
    """Test unsubscribe form"""
    print("\n🧪 Testing Unsubscribe Form...")
    
    # Test valid form
    form_data = {
        'email': 'subscriber1@example.com'  # This should exist from sample data
    }
    form = UnsubscribeForm(data=form_data)
    
    if form.is_valid():
        print("✅ Unsubscribe form validation passed")
        print(f"   Email: {form.cleaned_data['email']}")
    else:
        print("❌ Unsubscribe form validation failed")
        print(f"   Errors: {form.errors}")

def test_newsletter_form():
    """Test newsletter form"""
    print("\n🧪 Testing Newsletter Form...")
    
    # Test valid form
    form_data = {
        'title': 'Test Newsletter',
        'subject': 'Test Subject',
        'content': '<h1>Test Content</h1><p>This is a test newsletter.</p>',
        'is_scheduled': False
    }
    form = NewsletterForm(data=form_data)
    
    if form.is_valid():
        print("✅ Newsletter form validation passed")
        print(f"   Title: {form.cleaned_data['title']}")
        print(f"   Subject: {form.cleaned_data['subject']}")
    else:
        print("❌ Newsletter form validation failed")
        print(f"   Errors: {form.errors}")

def main():
    """Run all form tests"""
    print("🚀 Testing Newsletter Application Forms")
    print("=" * 50)
    
    test_subscription_form()
    test_unsubscribe_form()
    test_newsletter_form()
    
    print("\n" + "=" * 50)
    print("✅ Form testing completed!")

if __name__ == '__main__':
    main()
