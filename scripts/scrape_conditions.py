"""
Scraper extracting the list of conditions from the NSC legacy web site.

"""

import json
import re
import requests

from bs4 import BeautifulSoup

from nsc.condition.models import Condition


def run():
    index = load_index()
    for entry in index:
        page = get_page(entry['url'])

        try:
            obj = Condition.objects.get(slug=entry['slug'])
        except Condition.DoesNotExist:
            obj = Condition(slug=entry['slug'])

        obj.name = entry['name']
        obj.ages = entry['ages']
        obj.description = get_description(page)
        obj.save()


def load_index():
    with open('fixtures/legacy_index.json', 'r') as fp:
        return json.load(fp)


def get_page(url):
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def get_description(node):

    content = []

    regex = re.compile(r'^More about .*')
    node = node.find('h3', string=regex)
    node = node.next_sibling

    while node.name != 'h3':
        link = node.find('a')
        if link is None:
            text = node.text.strip()
            text += '\n{: class=govuk-body }'
            content.append(text)
        else:
            link_url = link['href']
            content.append('\n[%s](%s){: class="govuk-link"}' % ('Read more on NHS UK', link_url))
        node = node.find_next_sibling()

    return '\n'.join(content)
