"""
Scraper extracting the list of NSC policies from the legacy web site.

"""

import json
import re

import requests
from bs4 import BeautifulSoup

from nsc.policy.models import Policy


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
        obj.is_screened = entry["is_screened"]
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

    content = []

    regex = re.compile(r"^More about .*")
    node = node.find("h3", string=regex)
    node = node.next_sibling

    while node.name != "h3":
        link = node.find("a")
        if link is None:
            text = node.text.strip()
            if text:
                content.append(text)
        else:
            link_url = link["href"]
            link_text = link.text.strip()
            content.append("\n[%s](%s)" % (link_text, link_url))
        node = node.find_next_sibling()

    return "\n".join(content)
