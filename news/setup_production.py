#!/usr/bin/env python
"""
Production setup script for Django Newsletter Application
"""
import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def setup_email_config():
    """Guide user through email configuration"""
    print("\n📧 Email Configuration Setup")
    print("=" * 40)
    
    print("For production use, you need to configure email settings.")
    print("This guide will help you set up Gmail SMTP (recommended).")
    print("\n📋 Gmail Setup Instructions:")
    print("1. Enable 2-Factor Authentication on your Gmail account")
    print("2. Generate an App Password:")
    print("   - Go to Google Account settings")
    print("   - Security → 2-Step Verification → App passwords")
    print("   - Generate password for 'Mail'")
    print("3. Use the generated app password (not your regular password)")
    
    email = input("\n📧 Enter your Gmail address: ").strip()
    if not email:
        print("❌ Email address is required")
        return False
    
    app_password = input("🔑 Enter your Gmail app password: ").strip()
    if not app_password:
        print("❌ App password is required")
        return False
    
    from_email = input(f"📤 From email name (default: Newsletter App <{email}>): ").strip()
    if not from_email:
        from_email = f"Newsletter App <{email}>"
    
    site_url = input("🌐 Your website URL (default: http://localhost:8001): ").strip()
    if not site_url:
        site_url = "http://localhost:8001"
    
    # Update .env file
    env_content = f"""# Django Settings
SECRET_KEY=django-insecure-4)7c^x_ai4)nq)l)3w$rnlmrld4kw^9&k+00h_z-@k-2x81_(0
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Email Configuration (Production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER={email}
EMAIL_HOST_PASSWORD={app_password}
DEFAULT_FROM_EMAIL={from_email}

# Site Configuration
SITE_URL={site_url}

# Newsletter Settings (Production - require confirmation)
NEWSLETTER_REQUIRE_CONFIRMATION=True
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Email configuration saved to .env file")
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up Django Newsletter Application for Production")
    print("=" * 60)
    
    # Change to the project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Check if virtual environment exists
    if not os.path.exists('venv'):
        print("❌ Virtual environment not found. Please create one first:")
        print("   python -m venv venv")
        sys.exit(1)
    
    # Activate virtual environment command
    if os.name == 'nt':  # Windows
        activate_cmd = 'venv\\Scripts\\activate.bat &&'
    else:  # Unix/Linux/macOS
        activate_cmd = 'source venv/bin/activate &&'
    
    # Email configuration
    if not setup_email_config():
        print("❌ Email configuration failed")
        sys.exit(1)
    
    # Setup steps
    steps = [
        (f"{activate_cmd} pip install -r requirements.txt", "Installing dependencies"),
        (f"{activate_cmd} python manage.py migrate", "Running database migrations"),
        (f"{activate_cmd} python manage.py collectstatic --noinput", "Collecting static files"),
    ]
    
    # Run setup steps
    for command, description in steps:
        if not run_command(command, description):
            print(f"\n❌ Setup failed at: {description}")
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 Production setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start the Django server:")
    print("   python manage.py runserver")
    
    print("\n2. Start Celery worker (REQUIRED for email sending):")
    print("   celery -A newsletter_project worker --loglevel=info")
    
    print("\n3. Test the application:")
    print("   - Visit your site and subscribe with a real email")
    print("   - Check your email for confirmation")
    print("   - Confirm subscription and receive welcome email")
    
    print("\n4. Admin panel:")
    print("   - Create superuser: python manage.py createsuperuser")
    print("   - Access admin: /admin/")
    
    print("\n📧 Email Flow:")
    print("   Subscribe → Confirmation Email → Confirm → Welcome Email")
    
    print("\n⚠️  Important:")
    print("   - Celery worker MUST be running for emails to be sent")
    print("   - Check spam folder if emails don't arrive")
    print("   - Monitor Celery logs for email sending status")

if __name__ == '__main__':
    main()
