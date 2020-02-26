from django.utils import timezone


def get_today():
    return timezone.localtime(timezone.now()).date()
