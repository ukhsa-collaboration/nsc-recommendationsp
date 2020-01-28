"""
Scraper functions for extracting fixtures from the legacy web site.

"""

import json
import requests

from bs4 import BeautifulSoup
from django.utils import timezone
from django.utils.text import slugify

LEGACY_SITE = "https://legacyscreening.phe.org.uk"
TIMESTAMP = timezone.now().isoformat()


def run():
    save_policies(scrape_policy_list())


def save_fixture(name, data):
    with open('fixtures/%s' % name, 'w') as fixture_file:
        json.dump(data, fixture_file, indent=4)


def save_policies(data):
    save_fixture('policies.json', data)


def scrape_policy_list():
    response = requests.get(LEGACY_SITE + '/screening-recommendations.php')
    response.raise_for_status()
    return _scrape_policy_list(response.text)


def _scrape_policy_list(contents):
    soup = BeautifulSoup(contents, "lxml")
    results = []
    for idx, row in enumerate(_scrape_rows(soup)):
        results.extend(_scrape_row(row, idx + 1))
    return results


def _scrape_rows(node):
    return node.find('div', {'id': 'policyListArea'}).find_all('tr')


def _scrape_row(node, pk):
    cells = node.find_all('td')

    name = _scrape_policy_name(cells[1])
    slug = slugify(name)

    values = [
        {
            'model': 'core.condition',
            'pk': pk,
            'fields': {
                'created': TIMESTAMP,
                'modified': TIMESTAMP,
                'name': name,
                'slug': slug,
                'ages': _scrape_policy_ages(cells[2]),
                'description': '<h1>%s</h1>' % name,
                'markup': '# %s' % name
            }
        },
        {
            'model': 'core.policy',
            'pk': pk,
            'fields': {
                'created': TIMESTAMP,
                'modified': TIMESTAMP,
                'name': name,
                'slug': slug,
                'is_active': True,
                'is_screened': _scrape_policy_recommendation(cells[5]),
                'description': '<h1>%s</h1>' % name,
                'markup': '# %s' % name,
                'condition': pk
            }
        }
    ]

    return values


def _scrape_policy_name(node):
    return node.find('a').text.strip()


def _scrape_policy_ages(node):
    text = node.text.strip().lower()

    if ' and ' in text:
        text = text.replace(' and ', ' ')
    elif text == 'all age':
        text = 'all'

    return text.split()


def _scrape_policy_recommendation(node):
    node = node.find('img')
    if node:
        return 'not recommended' not in node['title']
    else:
        return None
