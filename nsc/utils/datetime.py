from django.utils import timezone

from dateutil.relativedelta import relativedelta


_day_endings = {1: "st", 2: "nd", 3: "rd", 21: "st", 22: "nd", 23: "rd", 31: "st"}


def get_today():
    return timezone.localtime(timezone.now()).date()


def from_today(offset):
    return get_today() + relativedelta(days=offset)


def get_day_display(day):
    if day is None:
        raise ValueError("The day cannot be None")
    if not 1 <= day <= 31:
        raise ValueError("The day must fall within a month")
    return str(day) + _day_endings.get(day, "th")


def get_date_display(date):
    if date is None:
        raise ValueError("The date cannot be None")
    return date.strftime("{D} %B %Y").replace("{D}", get_day_display(date.day))
