from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from newsletter.models import Newsletter
from subscribers.models import Subscriber
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Create sample data for testing the newsletter application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--subscribers',
            type=int,
            default=10,
            help='Number of sample subscribers to create (default: 10)',
        )
        parser.add_argument(
            '--newsletters',
            type=int,
            default=3,
            help='Number of sample newsletters to create (default: 3)',
        )

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(f'Created admin user: admin/admin123')
        
        # Create sample subscribers
        subscribers_created = 0
        for i in range(1, options['subscribers'] + 1):
            email = f'subscriber{i}@example.com'
            subscriber, created = Subscriber.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': f'User{i}',
                    'last_name': f'Test{i}',
                    'is_active': True,
                    'is_confirmed': True,
                    'date_confirmed': timezone.now(),
                }
            )
            if created:
                subscribers_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {subscribers_created} sample subscribers')
        )
        
        # Create sample newsletters
        newsletters_created = 0
        sample_newsletters = [
            {
                'title': 'Welcome to Our Newsletter!',
                'subject': 'Welcome! Here\'s what you can expect',
                'content': '''
                <h2>Welcome to Our Newsletter!</h2>
                <p>Thank you for subscribing to our newsletter. We're excited to have you on board!</p>
                <p>Here's what you can expect from us:</p>
                <ul>
                    <li>Weekly updates on industry news</li>
                    <li>Exclusive tips and tricks</li>
                    <li>Special offers and promotions</li>
                </ul>
                <p>Stay tuned for more great content!</p>
                <p>Best regards,<br>The Newsletter Team</p>
                '''
            },
            {
                'title': 'Monthly Industry Update',
                'subject': 'Your Monthly Industry Roundup',
                'content': '''
                <h2>Monthly Industry Update</h2>
                <p>Here are the top stories from this month:</p>
                <h3>🚀 Technology Trends</h3>
                <p>The latest developments in technology that are shaping our industry...</p>
                <h3>📊 Market Analysis</h3>
                <p>Key market insights and what they mean for your business...</p>
                <h3>💡 Tips & Tricks</h3>
                <p>Practical advice you can implement right away...</p>
                <p>Thank you for reading!</p>
                '''
            },
            {
                'title': 'Special Holiday Offer',
                'subject': '🎉 Exclusive Holiday Deal Inside!',
                'content': '''
                <h2>🎉 Special Holiday Offer!</h2>
                <p>The holidays are here, and we have something special for you!</p>
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; text-align: center; margin: 20px 0;">
                    <h3 style="color: #dc3545;">50% OFF</h3>
                    <p>Use code: <strong>HOLIDAY50</strong></p>
                    <p>Valid until December 31st</p>
                </div>
                <p>Don't miss out on this limited-time offer!</p>
                <p>Happy Holidays!</p>
                '''
            }
        ]
        
        for i, newsletter_data in enumerate(sample_newsletters[:options['newsletters']]):
            newsletter, created = Newsletter.objects.get_or_create(
                title=newsletter_data['title'],
                defaults={
                    'subject': newsletter_data['subject'],
                    'content': newsletter_data['content'],
                    'created_by': admin_user,
                }
            )
            if created:
                newsletters_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {newsletters_created} sample newsletters')
        )
        
        # Summary
        total_subscribers = Subscriber.objects.count()
        total_newsletters = Newsletter.objects.count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSample data creation complete!'
                f'\nTotal subscribers: {total_subscribers}'
                f'\nTotal newsletters: {total_newsletters}'
                f'\nAdmin user: admin/admin123'
            )
        )
