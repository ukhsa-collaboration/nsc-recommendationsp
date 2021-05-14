"""
Scraper extracting the latest reviews for each condition on the legacy
web site.

"""
import calendar
import datetime
import json
import re

from django.contrib.auth import get_user_model

import requests
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta

from nsc.policy.models import Policy
from nsc.review.models import Review, ReviewRecommendation
from scripts.parse import content_nodes, parse_html


def run():
    print("Scraping...")
    index = load_index()
    for entry in index:
        page = get_page(entry["url"])

        last_review_date = get_last_review_date(page)

        if last_review_date is None:
            print("  [skipping]", entry["name"])
            continue
        else:
            print(" ", entry["name"])

        review_end = last_review_date
        review_start = last_review_date + relativedelta(months=-6)

        name = "{0} {1}".format(entry["name"], review_start.year)

        try:
            review = Review.objects.get(name=name)
        except Review.DoesNotExist:
            review = Review(name=name, is_legacy=True)

        review.review_type = [Review.TYPE.other]

        review.review_start = review_start
        review.review_end = review_end
        review.user = get_user_model().objects.get_or_create(username="legacy")[0]

        if review.review_end:
            review.published = True

        review.summary = get_summary(page)

        review.clean()
        review.save()

        policy = Policy.objects.get(slug=entry["slug"])
        policy.next_review = last_review_date + relativedelta(years=3)
        policy.summary = review.summary

        policy.clean()
        policy.save()

        policy.reviews.add(review)

        ReviewRecommendation.objects.get_or_create(
            review=review,
            policy=policy,
            defaults={"recommendation": entry["recommendation"]},
        )

    print("Finished")


def load_index():
    with open("fixtures/legacy_index.json", "r") as fp:
        return json.load(fp)


def get_page(url):
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def get_last_review_date(node):
    node = node.find("strong", string="Last review completed")

    if not node:
        return None

    try:
        text = node.find_next("td").text.strip()
        timestamp = datetime.datetime.strptime(text, "%B %Y")
        first, last = calendar.monthrange(timestamp.year, timestamp.month)
        timestamp = timestamp.replace(day=last)
        return timestamp.date()
    except ValueError:
        return None


def get_summary(node):
    regex = re.compile(r"^Why is screening (not )?recommended by UK NSC\?")
    node = node.find("h3", string=regex)

    if node:
        node = node.next_sibling
        return parse_html(content_nodes(node))

    return ""
