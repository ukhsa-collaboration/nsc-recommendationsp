from nsc.utils import markdown


def test_heading_level_one_conversion():
    """
    Test level-one headings are converted with GDS extra-large heading class added.
    """
    text = markdown.convert("# Heading")
    assert text == '<h1 class="govuk-heading-xl">Heading</h1>'


def test_heading_level_two_conversion():
    """
    Test level-two headings are converted with GDS large heading class added.
    """
    text = markdown.convert("## Heading")
    assert text == '<h2 class="govuk-heading-l">Heading</h2>'


def test_heading_level_three_conversion():
    """
    Test level-three headings are converted with GDS medium heading class added.
    """
    text = markdown.convert("### Heading")
    assert text == '<h3 class="govuk-heading-m">Heading</h3>'


def test_heading_level_four_conversion():
    """
    Test level-two headings are converted with GDS small heading class added.
    """
    text = markdown.convert("#### Heading")
    assert text == '<h4 class="govuk-heading-s">Heading</h4>'


def test_paragraph_conversion():
    """
    Test paragraphs are converted with GDS class(es) added.
    """
    text = markdown.convert("Paragraph")
    assert text == '<p class="govuk-body">Paragraph</p>'


def test_embedded_link_conversion():
    """
    Test links are converted with GDS class(es) added.
    """
    text = markdown.convert("Visit [title](url).")
    assert (
        text
        == '<p class="govuk-body">Visit <a class="govuk-link" href="url">title</a>.</p>'
    )


def test_solitary_link_conversion():
    """
    Test links on a line by themselves are wrapped in paragraphs.
    """
    text = markdown.convert("[title](url)")
    assert (
        text == '<p class="govuk-body"><a class="govuk-link" href="url">title</a></p>'
    )
