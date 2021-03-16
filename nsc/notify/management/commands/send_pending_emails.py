from django.core.management import BaseCommand

from ...tasks import send_pending_emails


class Command(BaseCommand):
    def handle(self, *args, **options):
        send_pending_emails()
