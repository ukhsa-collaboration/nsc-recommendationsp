"""
Scraper extracting the list of NSC policies from the legacy web site.

"""

import json
import requests

from bs4 import BeautifulSoup
from django.utils import timezone
from django.utils.text import slugify

SITE = "https://legacyscreening.phe.org.uk/"
TIMESTAMP = timezone.now().isoformat()


def run():
    save_data(scrape_contents(get_page('screening-recommendations.php')))


def get_page(path):
    response = requests.get(SITE + path)
    response.raise_for_status()
    return response


def save_data(data):
    with open('fixtures/policies.json', 'w') as fixture_file:
        json.dump(data, fixture_file, indent=4)


def scrape_contents(response):
    results = []
    soup = BeautifulSoup(response.text, "lxml")
    for idx, row in enumerate(scrape_rows(soup)):
        results.append(scrape_row(row, idx + 1))
    return results


def scrape_rows(node):
    return node.find('div', {'id': 'policyListArea'}).find_all('tr')


def scrape_row(node, pk):
    fields = node.find_all('td')

    name = get_name(fields[1])
    slug = slugify(name)
    recommendation = get_recommendation(fields[6])

    return {
        'model': 'policy.policy',
        'pk': pk,
        'fields': {
            'created': TIMESTAMP,
            'modified': TIMESTAMP,
            'name': name,
            'slug': slug,
            'is_active': True,
            'is_screened': recommendation,
            'description': '<h1>%s</h1>' % name,
            'markup': '# %s' % name,
            'condition': pk
        }
    }


def get_name(node):
    return node.find('a').text.strip()


def get_recommendation(node):
    return 'not recommended' not in node.text
