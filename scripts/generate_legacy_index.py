"""
Generate an initial table of policies by scraping the legacy site.

"""

import json
import requests

from bs4 import BeautifulSoup
from django.utils import timezone
from django.utils.text import slugify

SITE = "https://legacyscreening.phe.org.uk"
TIMESTAMP = timezone.now().isoformat()


def run():
    save_data(scrape_contents(get_page('/screening-recommendations.php')))


def get_page(path):
    response = requests.get(SITE + path)
    response.raise_for_status()
    return response


def save_data(data):
    with open('fixtures/legacy_index.json', 'w') as fixture_file:
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
    url = get_url(fields[1])
    slug = slugify(name)
    ages = get_ages(fields[2])
    recommendation = get_recommendation(fields[6])

    return {
        'name': name,
        'slug': slug,
        'url': url,
        'ages': ages,
        'is_active': True,
        'is_screened': recommendation,
    }


def get_name(node):
    return node.find('a').text.strip()


def get_url(node):
    return SITE + node.find('a')['href']


def get_ages(node):
    text = node.text.strip().lower()

    if ' and ' in text:
        text = text.replace(' and ', ' ')
    elif text == 'all age':
        text = 'all'

    return text.split()


def get_recommendation(node):
    return 'not recommended' not in node.text
