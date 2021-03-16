from django.core.management import BaseCommand

from ...tasks import send_published_notifications


class Command(BaseCommand):
    def handle(self, *args, **options):
        send_published_notifications()
