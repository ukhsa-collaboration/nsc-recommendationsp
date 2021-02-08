from django.db.models import Count

import celery

from .models import Review


@celery.task
def send_open_review_notifications():
    open_reviews = Review.objects.consultation_open()
    open_reviews_without_notifications = open_reviews.annotate(
        notifications_count=Count("open_consultation_notifications"),
    ).filter(notifications_count=0)

    for review in open_reviews_without_notifications:
        review.send_open_consultation_notifications()
