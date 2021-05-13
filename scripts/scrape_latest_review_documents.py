"""
Scraper extracting the documents associated with the latest review, if
available, for each condition on the NSC legacy web site.

"""
import json
import os
import re
import tempfile

from django.core.files import File

import requests
from bs4 import BeautifulSoup

from nsc.document.models import Document
from nsc.policy.models import Policy

from .generate_legacy_index import SITE


def run():
    print("Scraping...")
    index = load_index()
    for entry in index:
        policy = Policy.objects.get(slug=entry["slug"])
        review = policy.reviews.published().first()

        if not review:
            print("  [skipping]", entry["name"])
            continue

        page = get_page(entry["url"])

        docs = list(get_documents(page))
        if docs:
            print(" ", entry["name"])
            review.documents.all().delete()
        else:
            print("  [skipping]", entry["name"])
            continue

        for doc_type, url in docs:
            add_doc(review, doc_type, url)

    print("Finished")


def load_index():
    with open("fixtures/legacy_index.json", "r") as fp:
        return json.load(fp)


def get_page(url):
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def get_documents(page):
    docs_label_node = page.find("td", string=re.compile("^Key downloads.*"))
    if docs_label_node is None:
        return

    listing_node = docs_label_node.find_next("td")
    document_links = listing_node.find_all("a")

    for link in document_links:
        doc_type = get_document_type(link.text)

        if doc_type is not None:
            yield doc_type, SITE + link["href"]


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


def get_document_type(label):
    label_lower = label.lower()

    if (
        "evidence summary" in label_lower
        or "evidence review" in label_lower
        or "uk nsc pilot triage" in label_lower
    ):
        return Document.TYPE.evidence_review
    elif "evidence map" in label_lower:
        return Document.TYPE.evidence_map
    elif "coversheet" in label_lower:
        return Document.TYPE.cover_sheet
    elif "cost effectiveness" in label_lower:
        return Document.TYPE.cost

    return Document.TYPE.other


def add_doc(review, document_type, document_url):
    document = Document.objects.create(document_type=document_type, review=review)
    add_file(document_url, document)

    return document
