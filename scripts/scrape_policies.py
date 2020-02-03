"""
Scraper extracting the list of NSC policies from the legacy web site.

"""

import json
import requests

from bs4 import BeautifulSoup

from nsc.condition.models import Condition
from nsc.policy.models import Policy


def run():
    index = load_index()
    for entry in index:
        # Todo re-enable to scrape content
        # page = get_page(entry['url'])

        try:
            obj = Policy.objects.get(slug=entry['slug'])
        except Policy.DoesNotExist:
            obj = Policy(slug=entry['slug'])

        obj.name = entry['name']
        obj.is_active = entry['is_active']
        obj.is_screened = entry['is_screened']
        # Todo re-enable to scrape content
        obj.markup = ''  # get_description(page)

        if obj.condition:
            assert obj.condition.slug == obj.slug
        else:
            obj.condition = Condition.objects.get(slug=obj.slug)

        obj.save()


def load_index():
    with open('fixtures/legacy_index.json', 'r') as fp:
        return json.load(fp)


def get_page(url):
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def get_description(node):
    return ''
