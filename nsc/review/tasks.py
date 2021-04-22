from django.db.models import Count

from ..celery import app
from .models import Review


@app.task
def send_open_review_notifications():
    open_reviews = Review.objects.consultation_open()
    open_reviews_without_notifications = open_reviews.annotate(
        notifications_count=Count("open_consultation_notifications"),
    ).filter(notifications_count=0)

    for review in open_reviews_without_notifications:
        review.send_open_consultation_notifications()


@app.task
def send_published_notifications():
    published_reviews = Review.objects.published().exclude_legacy()
    published_reviews_without_notifications = published_reviews.annotate(
        notifications_count=Count("decision_published_notifications"),
    ).filter(notifications_count=0)

    for review in published_reviews_without_notifications:
        review.send_decision_notifications()
