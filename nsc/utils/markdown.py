import markdown


def convert(content):
    return markdown.markdown(content, extensions=["attr_list"])
