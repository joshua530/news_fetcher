import re
import string


def format_data(data: list, type: str) -> str:
    """
    Converts list of results into a given format

    The only implemented types are xml, text and yaml
    """
    valid_types = "xml", "text", "yaml"
    type = type.lower()
    if type not in valid_types:
        raise ValueError(
            "Invalid type %s given. Valid types are xml, text and yaml" % (type)
        )

    if type == "xml":
        formatted_data = format_xml(data)
    elif type == "text":
        formatted_data = format_plain_text(data)
    elif type == "yaml":
        formatted_data = format_yaml(data)

    return formatted_data


def format_xml(data: list) -> str:
    all_results = '<?xml version="1.0" encoding="UTF-8"?>\n<results>\n'
    result_shell = (
        "<result>\n<title>{title}</title>\n<breadcrumb_url>{breadcrumb_url}</breadcrumb_url>\n"
        "<description>{description}</description>\n<site_links>{site_links}</site_links>\n</result>"
    )
    site_link_shell = "<link><name>{name}</name><url>{url}</url></link>"

    for result in data:
        # compile links
        tmp_links = ""
        for link in result["site_links"]:
            tmp_link = site_link_shell.format(name=link["name"], url=link["url"])
            tmp_links += tmp_link + "\n"
        if tmp_links != "":
            tmp_links = "\n" + tmp_links

        # compile single result
        tmp_result = result_shell.format(
            title=result["title"],
            breadcrumb_url=result["breadcrumb_url"],
            description=result["description"],
            site_links=tmp_links,
        )
        all_results += tmp_result + "\n"
    all_results += "</results>\n"
    return all_results


def format_plain_text(data: list) -> str:
    all_results = ""

    result_skeleton = (
        '"title": "{title}";\n"breadcrumb_url": "{breadcrumb_url}";\n'
        '"description": "{desc}";\n"site_links":{site_links}\n;;\n'
    )
    site_link_skeleton = '"name": "{name}", "url": "{url}";'

    for result in data:
        # compile links
        tmp_site_links = "\n"
        for link in result["site_links"]:
            current_link = site_link_skeleton.format(name=link["name"], url=link["url"])
            tmp_site_links += current_link + "\n"
        tmp_site_links = tmp_site_links.rstrip()

        #  fill in the skeleton
        tmp_placeholder = result_skeleton.format(
            title=result["title"],
            breadcrumb_url=result["breadcrumb_url"],
            desc=result["description"],
            site_links=tmp_site_links,
        )
        all_results += tmp_placeholder + "\n"

    # remove unwanted newline from the end of the string
    all_results = all_results.strip()
    all_results += "\n"

    return all_results


def format_yaml(data: list) -> str:
    """
    Converts fetched data into YAML

    Tab size is two spaces
    """
    tab = "  "
    two_tabs = tab * 2
    three_tabs = tab * 3
    four_tabs = tab * 4
    five_tabs = tab * 5
    six_tabs = tab * 6

    yaml_skel = f"results:\n{tab}result:\n"
    result_skel = (
        "{tab_2}- title: {title}\n"
        "{tab_3}breadcrumb_url: {breadcrumb_url}\n"
        "{tab_3}description: >-\n{description}\n"
        "{tab_3}site_links:{links}"
    )
    link_skel = "{tab_5}- name: {name}\n" "{tab_6}url: {url}"

    for result in data:
        # compile links
        tmp_links = ' ""\n'
        if len(result["site_links"]) > 0:
            tmp_links = ""
            tmp_links += "\n" + four_tabs + "link:\n"
            for link in result["site_links"]:
                tmp_links += (
                    link_skel.format(
                        tab_5=five_tabs,
                        name=quote_str_with_special_chars(link["name"]),
                        tab_6=six_tabs,
                        url=quote_str_with_special_chars(link["url"]),
                    )
                    + "\n"
                )

        # compile result
        tmp_result = (
            result_skel.format(
                tab_2=two_tabs,
                tab_3=three_tabs,
                title=quote_str_with_special_chars(result["title"]),
                breadcrumb_url=quote_str_with_special_chars(result["breadcrumb_url"]),
                description=format_description(
                    quote_str_with_special_chars(result["description"]), 4
                ),
                links=tmp_links,
            )
            + "\n"
        )
        # add result to whole set of results
        yaml_skel += tmp_result
    # remove unwanted new line character at the end
    yaml_skel = yaml_skel[:-1]
    return yaml_skel


def quote_str_with_special_chars(the_string: str) -> str:
    """
    Encloses string with special characters in double quotes
    """
    special_chars = ":{}[]&*#?|-><!%@`"
    for char in special_chars:
        if the_string.find(char) != -1:
            the_string = '"{}"'.format(the_string)
            break
    return the_string


def format_description(
    description: str, num_tabs: int, tab: str = "  ", line_len: int = 80
) -> str:
    """
    Formats a given result's description for consistency

    A tab consists of two spaces by default
    """
    # replace new line characters with spaces to avoid breaking
    # up string into unneccessary lines
    tmp_description = description.replace("\n", " ")

    if len(tmp_description) < line_len:
        return tab * num_tabs + tmp_description

    segments = []
    # Split sentence at intervals
    # If we are going to split a word at current position, move back, look
    # for the beginning of the word, and perform split before the
    # word begins
    current = 0
    while current < len(tmp_description):
        next_breaking_point = current + line_len

        # ensure we don't break a word into two or carry over punctuation mark to the next line
        if not tmp_description[next_breaking_point].isspace():
            # seek the nearest index that will help us split the sentence appropriately
            while (
                tmp_description[next_breaking_point].isalnum()
                or tmp_description[next_breaking_point] in string.punctuation
            ):
                next_breaking_point -= 1

        # split the sentence at the current position and seek the next splitting point
        segments.append(tmp_description[current : next_breaking_point + 1])
        next_breaking_point += 1

        # ensure the next splitting point isn't past the end of the sentence
        if next_breaking_point + line_len >= len(tmp_description):
            segments.append(tmp_description[next_breaking_point:])
            current = next_breaking_point + line_len
        else:
            current = next_breaking_point

    # remove whitespace from the start and end of split segments
    # remove multiple spaces from within the segments
    # append tabs for formatting
    for i in range(len(segments)):
        segments[i] = segments[i].strip()
        segments[i] = re.sub(r"(\s)\s+", r"\g<1>", segments[i])
        segments[i] = (tab * num_tabs) + segments[i]

    formatted_string = "\n".join(segments)
    return formatted_string
