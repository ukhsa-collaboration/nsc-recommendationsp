"""
Scraper extracting the documents associated with the latest review, if
available, for each condition on the NSC legacy web site.

"""
import json
import os
import re
import tempfile

import requests
from bs4 import BeautifulSoup
from django.core.files import File

from nsc.document.models import Document
from nsc.policy.models import Policy
from nsc.review.models import Review

from .generate_legacy_index import SITE


def run():
    print("Scraping...")
    index = load_index()
    for entry in index:
        policy = Policy.objects.get(slug=entry["slug"])
        review = Review.objects.for_policy(policy).published().first()

        if not review:
            print("  [skipping]", entry["name"])
            continue

        page = get_page(entry["url"])
        document_url = get_external_review_url(page)

        if not document_url:
            print("  [skipping]", entry["name"])
            continue

        print(" ", entry["name"])

        document = Document.objects.for_review(review).external().first()

        if not document:
            document = add_external_review(review)

        add_file(document_url, document)

    print("Finished")


def load_index():
    with open("fixtures/legacy_index.json", "r") as fp:
        return json.load(fp)


def get_page(url):
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def get_external_review_url(node):
    regex = re.compile(r"^Last external review.*")
    node = node.find("a", string=regex)
    return SITE + node["href"] if node else None


def get_name(filename):
    basename = os.path.basename(filename)
    name, ext = os.path.splitext(basename)
    return name.replace("_", " ").replace("-", " ")


def add_file(url, document):
    response = requests.get(url)
    header = response.headers["content-disposition"]
    filename = re.findall("filename=(.+)", header)[0]

    with tempfile.TemporaryFile() as fp:
        fp.write(response.content)
        fp.seek(0)
        document.name = get_name(filename)
        document.upload.save(filename, File(fp), save=True)
        document.save()


def add_external_review(review):
    document = Document()
    document.document_type = Document.TYPE.external_review
    document.review = review
    document.save()
    return document
