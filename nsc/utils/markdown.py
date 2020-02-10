from bs4 import BeautifulSoup

import markdown


_conversions = {
    "h1": {"classes": ["govuk-heading-xl"]},
    "h2": {"classes": ["govuk-heading-l"]},
    "h3": {"classes": ["govuk-heading-m"]},
    "h4": {"classes": ["govuk-heading-s"]},
    "p": {"classes": ["govuk-body"]},
    "a": {"classes": ["govuk-link"]},
}


def convert(content):
    """
    Generate HTML from markdown and add GDS classes.
    """
    soup = BeautifulSoup(markdown.markdown(content), "html.parser")
    for tag, updates in _conversions.items():
        for node in soup.find_all(tag):
            existing_classes = node.get("class", [])
            for css_class in updates["classes"]:
                if css_class not in existing_classes:
                    existing_classes.append(css_class)
            node["class"] = existing_classes

    return str(soup)
