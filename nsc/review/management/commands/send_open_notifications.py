from django.core.management import BaseCommand

from ...tasks import send_open_review_notifications


class Command(BaseCommand):
    def handle(self, *args, **options):
        send_open_review_notifications()
