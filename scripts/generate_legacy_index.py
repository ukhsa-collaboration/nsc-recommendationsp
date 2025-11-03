"""
Generate an initial table of policies by scraping the legacy site.

"""

import json
import time
from urllib.parse import urljoin

from django.utils import timezone
from django.utils.text import slugify

import requests
from bs4 import BeautifulSoup


SITE = "https://view-health-screening-recommendations.service.gov.uk"
TIMESTAMP = timezone.now().isoformat()


def run():
    save_data(scrape_contents())


def get_page(url):
    response = requests.get(url)
    response.raise_for_status()
    return response


def save_data(data):
    with open("fixtures/legacy_index.json", "w") as fixture_file:
        json.dump(data, fixture_file, indent=4)


def scrape_contents():
    url = SITE
    print("Scraping contents...", url)
    results = []
    while url:
        response = get_page(url)
        url = str(response)
        soup = BeautifulSoup(response.text, "lxml")
        for idx, row in enumerate(scrape_rows(soup)):
            results.append(scrape_row(row, idx + 1))
        next_link = soup.select_one('a[rel="next"], a:-soup-contains("Next")')
        if next_link and next_link.has_attr("href"):
            url = urljoin(url, next_link["href"])
        else:
            url = None
    return results


def scrape_rows(node):
    return node.select("tr:has(td)")


def scrape_row(node, pk):
    fields = node.find_all("td")
    name = get_name(fields[0])
    url = get_url(fields[0])
    slug = slugify(name)
    ages = get_ages(fields[1])
    recommendation = get_recommendation(fields[3])
    return {
        "name": name,
        "slug": slug,
        "url": url,
        "ages": ages,
        "is_active": True,
        "recommendation": recommendation,
    }


def get_name(node):
    return node.find("a").text.strip()


def get_url(node):
    return SITE + node.find("a")["href"]


def get_ages(node):
    text = node.text.strip().lower()

    if " and " in text:
        text = text.replace(" and ", " ")
    elif text == "all ages":
        text = "all"

    return text.split(", ")


def get_recommendation(node):
    return "not recommended" not in node.text
