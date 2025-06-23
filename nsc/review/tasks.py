import logging

from django.core.cache import cache
from django.db.models import Count

from ..celery import app
from .models import Review


logger = logging.getLogger(__name__)


@app.task
def send_open_review_notifications():
    open_reviews = Review.objects.consultation_open().exclude_legacy()
    open_reviews_without_notifications = open_reviews.annotate(
        notifications_count=Count("open_consultation_notifications"),
    ).filter(notifications_count=0)

    for review in open_reviews_without_notifications:
        review.send_open_consultation_notifications()

    # if we have sent any notifications clear the cache
    if len(open_reviews_without_notifications) > 0:
        cache.clear()


@app.task
def send_published_notifications():
    published_reviews = Review.objects.published().exclude_legacy()
    published_reviews_without_notifications = published_reviews.annotate(
        notifications_count=Count("decision_published_notifications"),
    ).filter(notifications_count=0)

    logger.info(
        f"CELERY TASK STARTED: Found {published_reviews_without_notifications.count()} reviews needing emails"
    )

    for review in published_reviews_without_notifications:
        logger.info(f"Processing review: {review.name}")
        review.send_decision_notifications()

    # if we have sent any notifications clear the cache
    if len(published_reviews_without_notifications) > 0:
        cache.clear()
