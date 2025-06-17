#!/usr/bin/env python
"""
Template validation script for The Idea Engine
"""
import os
import django
import re

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsletter_project.settings')
django.setup()

from django.template.loader import render_to_string, get_template
from django.template import TemplateDoesNotExist
from subscribers.forms import SubscriptionForm, UnsubscribeForm
from newsletter.forms import NewsletterForm
from subscribers.models import Subscriber
from newsletter.models import Newsletter

def validate_html_structure(html_content, template_name):
    """Validate basic HTML structure"""
    issues = []
    
    # Check for basic HTML structure
    if not re.search(r'<!DOCTYPE html>', html_content, re.IGNORECASE):
        if 'email' not in template_name:  # Email templates might not have DOCTYPE
            issues.append("Missing DOCTYPE declaration")
    
    # Check for balanced tags
    open_tags = re.findall(r'<(\w+)[^>]*>', html_content)
    close_tags = re.findall(r'</(\w+)>', html_content)
    
    # Remove self-closing tags
    self_closing = ['img', 'br', 'hr', 'input', 'meta', 'link']
    open_tags = [tag for tag in open_tags if tag.lower() not in self_closing]
    
    # Check if tags are balanced
    for tag in set(open_tags):
        open_count = open_tags.count(tag)
        close_count = close_tags.count(tag)
        if open_count != close_count:
            issues.append(f"Unbalanced {tag} tags: {open_count} open, {close_count} close")
    
    return issues

def main():
    print("🧪 The Idea Engine - Template Validation")
    print("=" * 50)
    
    # Templates to validate
    templates_to_test = [
        ('newsletter/home.html', {'form': SubscriptionForm()}),
        ('subscribers/subscribe.html', {'form': SubscriptionForm()}),
        ('subscribers/unsubscribe.html', {'form': UnsubscribeForm()}),
        ('subscribers/subscription_success.html', {}),
        ('subscribers/unsubscribe_success.html', {}),
        ('base.html', {}),
    ]
    
    total_issues = 0
    
    for template_name, context in templates_to_test:
        print(f"\n🔍 Validating {template_name}...")
        
        try:
            # Render template
            html_content = render_to_string(template_name, context)
            
            # Validate HTML structure
            issues = validate_html_structure(html_content, template_name)
            
            if issues:
                print(f"⚠️  Found {len(issues)} issues:")
                for issue in issues:
                    print(f"   - {issue}")
                total_issues += len(issues)
            else:
                print("✅ No issues found")
                
        except Exception as e:
            print(f"❌ Error rendering template: {str(e)}")
            total_issues += 1
    
    print("\n" + "=" * 50)
    if total_issues == 0:
        print("🎉 All templates validated successfully!")
        print("✅ No HTML structure issues found")
        print("✅ All templates render correctly")
        print("✅ The Idea Engine is ready to use!")
    else:
        print(f"⚠️  Found {total_issues} total issues")
        print("🔧 Please review and fix the issues above")
    
    print("\n📱 Test URLs:")
    print("- Home: http://127.0.0.1:8002/")
    print("- Subscribe: http://127.0.0.1:8002/subscribe/")
    print("- Unsubscribe: http://127.0.0.1:8002/unsubscribe/")
    print("- Admin: http://127.0.0.1:8002/admin/")

if __name__ == '__main__':
    main()
