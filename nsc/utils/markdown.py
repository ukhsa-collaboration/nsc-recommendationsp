import bleach
import markdown
from bleach_whitelist import markdown_attrs, markdown_tags
from bs4 import BeautifulSoup


_conversions = {
    "h1": {"classes": ["govuk-heading-xl"]},
    "h2": {"classes": ["govuk-heading-l"]},
    "h3": {"classes": ["govuk-heading-m"]},
    "h4": {"classes": ["govuk-heading-s"]},
    "p": {"classes": ["govuk-body"]},
    "a": {"classes": ["govuk-link"]},
    "ul": {"classes": ["govuk-list", "govuk-list--bullet"]},
    "ol": {"classes": ["govuk-list", "govuk-list--number"]},
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

    # sanitize the output markdown so that people can't inject dangerous content
    valid_attrs = dict(markdown_attrs)
    valid_attrs["*"].append("class")
    return bleach.clean(str(soup), markdown_tags, markdown_attrs)
