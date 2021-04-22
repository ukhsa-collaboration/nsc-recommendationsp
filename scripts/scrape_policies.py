"""
Scraper extracting the list of NSC policies from the legacy web site.

"""

import json
import re

import requests
from bs4 import BeautifulSoup

from nsc.policy.models import Policy
from scripts.parse import content_nodes, parse_html


def run():
    print("Scraping...")
    index = load_index()
    for entry in index:
        print(" ", entry["name"])

        page = get_page(entry["url"])

        try:
            obj = Policy.objects.get(slug=entry["slug"])
        except Policy.DoesNotExist:
            obj = Policy(slug=entry["slug"])

        obj.name = entry["name"]
        obj.is_active = entry["is_active"]
        obj.recommendation = entry["recommendation"]
        obj.ages = entry["ages"]
        obj.condition = get_condition(page)
        obj.keywords = ""

        obj.clean()

        obj.save()

    print("Finished")


def load_index():
    with open("fixtures/legacy_index.json", "r") as fp:
        return json.load(fp)


def get_page(url):
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def get_condition(node):
    regex = re.compile(r"^More about .*")
    node = node.find("h3", string=regex)

    if node:
        node = node.next_sibling
        return parse_html(content_nodes(node))

    return ""
