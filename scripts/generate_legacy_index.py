import json
import time
import requests
from bs4 import BeautifulSoup

SITE = "https://legacyscreening.phe.org.uk"
INDEX_URL = f"{SITE}/screening-recommendations.php"
FIXTURE_PATH = "fixtures/legacy_index.json"

def get_page(url):
    print(f"Fetching: {url}")
    response = requests.get(url)
    response.raise_for_status()
    return response

def get_total_pages(soup):
    print("Detecting total pages...")
    pagination_links = soup.select("nav[role='navigation'] .pagination__item a")
    page_numbers = []

    for link in pagination_links:
        text = link.text.strip()
        if text.isdigit():
            page_numbers.append(int(text))

    max_page = max(page_numbers) if page_numbers else 1
    print(f"Total pages found: {max_page}")
    return max_page

def scrape_rows(soup):
    main = soup.find("main", id="main-content")
    if not main:
        print("<main id='main-content'> not found.")
        return []
    table = main.find("table", class_="govuk-table")
    if not table:
        print("<table class='govuk-table'> not found.")
        return []
    return table.find("tbody").find_all("tr")

def get_name(node):
    link = node.find("a")
    return link.text.strip() if link else "Unnamed"

def get_url(node):
    link = node.find("a")
    return SITE + link["href"] if link and link.has_attr("href") else ""

def get_ages(node):
    text = node.text.strip().lower()
    if " and " in text:
        text = text.replace(" and ", " ")
    elif text == "all age":
        text = "all"
    return text.split()

def get_recommendation(node):
    return "not recommended" not in node.text.lower()

def scrape_row(row):
    fields = row.find_all("td")
    if len(fields) < 3:
        print("Skipping row: not enough <td> fields")
        return None
    return {
        "name": get_name(fields[0]),
        "slug": get_url(fields[0]).split("/")[-2],
        "url": get_url(fields[0]),
        "ages": get_ages(fields[1]),
        "is_active": True,
        "recommendation": get_recommendation(fields[2]),
    }

def run():
    print("Starting generate_legacy_index")
    all_items = {}
    first_response = get_page(INDEX_URL)
    soup = BeautifulSoup(first_response.text, "lxml")
    total_pages = get_total_pages(soup)
    print(f"Total pages found: {total_pages}")

    for page in range(1, total_pages + 1):
        url = f"{INDEX_URL}?page={page}"
        response = get_page(url)
        soup = BeautifulSoup(response.text, "lxml")
        rows = scrape_rows(soup)
        print(f"Found {len(rows)} rows on page {page}")
        for row in rows:
            item = scrape_row(row)
            if item:
                all_items[item["slug"]] = item  # Deduplicate by slug
        time.sleep(0.5)

    unique_items = {item["slug"]: item for item in all_items}
    with open(FIXTURE_PATH, "w") as f:
        json.dump(list(unique_items.values()), f, indent=2)
        print(f"Saved {len(unique_items)} unique policies to {FIXTURE_PATH}")
