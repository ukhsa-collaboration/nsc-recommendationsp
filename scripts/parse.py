import html2markdown


def strip_attributes(attrs):
    # if we hit an attribute html2markdown doesn't like no parsing is done so we remove them here as
    # they only alpply in the legacy context
    return {
        k: v
        for k, v in attrs.items()
        if k in ["href", "src", "alt"]
    }


def node_is_parsable(node):
    # This is a list of tags that we replace with the child content as the html2markdown lib can't handle them
    # While we should be able to generate tables in the markdown, the tables used on the legacy content appears
    # to be for alignment purposes only with a single element so we can instead just use the child content
    unparsed_tags = ["div", "span", "table", "tbody", "tr", "td", "th"]

    if isinstance(node, str):
        return True

    return (
        node.name not in unparsed_tags and node.text.strip() != ""
    )


def parse_html(nodes):
    content = []
    for node in nodes:
        node.attrs = strip_attributes(getattr(node, "attrs", {}))

        # for each descendant in the tree, clean it and remove any unparsed tags
        if hasattr(node, "find_all"):
            for child in node.find_all():
                child.attrs = strip_attributes(getattr(child, "attrs", {}))

                if not node_is_parsable(child):
                    child.replace_with_children()

        if not node_is_parsable(node.name):
            # if the current node is unparsable run the parser on the children
            content.append(parse_html(node.children))
        else:
            content.append(html2markdown.convert(str(node)).replace("&nbsp;", " "))

    return "\n\n".join(block for block in content if block.strip() != "")


def content_nodes(first_node):
    node = first_node
    while node.name != "h3":
        yield node
        node = node.find_next_sibling()
