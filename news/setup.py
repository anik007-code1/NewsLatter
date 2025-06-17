#!/usr/bin/env python
"""
Setup script for Django Newsletter Application
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

def main():
    """Main setup function"""
    print("🚀 Setting up Django Newsletter Application")
    print("=" * 50)
    
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
    
    # Setup steps
    steps = [
        (f"{activate_cmd} pip install -r requirements.txt", "Installing dependencies"),
        (f"{activate_cmd} python manage.py migrate", "Running database migrations"),
        (f"{activate_cmd} python manage.py collectstatic --noinput", "Collecting static files"),
        (f"{activate_cmd} python manage.py create_sample_data", "Creating sample data"),
    ]
    
    # Run setup steps
    for command, description in steps:
        if not run_command(command, description):
            print(f"\n❌ Setup failed at: {description}")
            sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start the Django server:")
    print("   python run_server.py")
    print("   OR")
    print("   source venv/bin/activate && python manage.py runserver")
    print("\n2. Visit http://127.0.0.1:8000 in your browser")
    print("\n3. Admin panel: http://127.0.0.1:8000/admin/")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n4. (Optional) Start Celery for background tasks:")
    print("   python run_celery.py")
    print("   OR")
    print("   source venv/bin/activate && celery -A newsletter_project worker --loglevel=info")
    print("\n📚 Check README.md for more detailed instructions")

if __name__ == '__main__':
    main()
