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
    save_conditions(scrape_condition_list())


def save_fixture(name, data):
    with open('fixtures/conditions.json', 'w') as fixture_file:
        json.dump(data, fixture_file, indent=4)


def save_conditions(data):
    save_fixture('conditions.json', data)


def scrape_condition_list():
    response = requests.get(LEGACY_SITE + '/screening-recommendations.php')
    response.raise_for_status()
    return _scrape_list(response.text)


def _scrape_list(contents):
    soup = BeautifulSoup(contents, "lxml")
    results = []
    for idx, row in enumerate(_scrape_rows(soup)):
        results.append(_scrape_row(row, idx + 1))
    return results


def _scrape_rows(node):
    return node.find('div', {'id': 'policyListArea'}).find_all('tr')


def _scrape_row(node, pk):
    cells = node.find_all('td')

    values = {
        'model': 'core.condition',
        'pk': pk,
        'fields': {
            'created': TIMESTAMP,
            'modified': TIMESTAMP,
            'is_active': True,
            'name': _scrape_condition_name(cells[1]),
            'ages': _scrape_condition_ages(cells[2]),
            'is_screened': _scrape_recommendation(cells[5])
        }
    }

    values['fields']['slug'] = slugify(values['fields']['name'])

    return values

def _scrape_condition_name(node):
    return node.find('a').text.strip()


def _scrape_condition_url(node):
    return LEGACY_SITE + node.find('a')['href'].strip()


def _scrape_condition_ages(node):
    text = node.text.strip().lower()

    if ' and ' in text:
        text = text.replace(' and ', ' ')
    elif text == 'all age':
        text = 'all'

    return text.split()


def _scrape_recommendation(node):
    node = node.find('img')
    if node:
        return 'not recommended' not in node['title']
    else:
        return None
