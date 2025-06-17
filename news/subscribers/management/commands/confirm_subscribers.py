from django.core.management.base import BaseCommand
from subscribers.models import Subscriber


class Command(BaseCommand):
    help = 'Manually confirm pending subscribers (for testing purposes)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Confirm specific email address',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Confirm all pending subscribers',
        )

    def handle(self, *args, **options):
        if options['email']:
            # Confirm specific email
            try:
                subscriber = Subscriber.objects.get(email=options['email'], is_confirmed=False)
                subscriber.confirm_subscription()
                self.stdout.write(
                    self.style.SUCCESS(f'Confirmed subscription for {subscriber.email}')
                )
            except Subscriber.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'No pending subscription found for {options["email"]}')
                )
        
        elif options['all']:
            # Confirm all pending subscribers
            pending_subscribers = Subscriber.objects.filter(is_confirmed=False)
            count = 0
            for subscriber in pending_subscribers:
                subscriber.confirm_subscription()
                count += 1
                self.stdout.write(f'Confirmed: {subscriber.email}')
            
            self.stdout.write(
                self.style.SUCCESS(f'Confirmed {count} pending subscriptions')
            )
        
        else:
            # Show pending subscribers
            pending_subscribers = Subscriber.objects.filter(is_confirmed=False)
            if pending_subscribers.exists():
                self.stdout.write('Pending subscribers:')
                for subscriber in pending_subscribers:
                    self.stdout.write(f'  - {subscriber.email} (subscribed: {subscriber.date_subscribed})')
                self.stdout.write('\nUse --all to confirm all, or --email <email> to confirm specific subscriber')
            else:
                self.stdout.write(self.style.SUCCESS('No pending subscribers found'))
