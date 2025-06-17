from django.core.management.base import BaseCommand
from django.utils import timezone
from newsletter.models import Newsletter


class Command(BaseCommand):
    help = 'Send scheduled newsletters that are due'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show which newsletters would be sent without actually sending them',
        )

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Find newsletters that are scheduled and due to be sent
        due_newsletters = Newsletter.objects.filter(
            is_scheduled=True,
            scheduled_date__lte=now,
            is_sent=False
        )
        
        if not due_newsletters.exists():
            self.stdout.write(
                self.style.SUCCESS('No scheduled newsletters are due to be sent.')
            )
            return
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No newsletters will actually be sent')
            )
            for newsletter in due_newsletters:
                self.stdout.write(
                    f'Would send: "{newsletter.title}" (scheduled for {newsletter.scheduled_date})'
                )
            return
        
        sent_count = 0
        for newsletter in due_newsletters:
            try:
                # Send the newsletter directly
                from newsletter.tasks import send_newsletter_direct
                send_newsletter_direct(newsletter.id)
                sent_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Sent newsletter "{newsletter.title}" successfully'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed to queue newsletter "{newsletter.title}": {str(e)}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully sent {sent_count} newsletters'
            )
        )
