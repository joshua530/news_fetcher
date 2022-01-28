# from request import get
import string
import re
from test_result import expected
import os
from bs4 import BeautifulSoup

# response = get(['news', 'latest', 'entertainment'])


def parse_response(html_str: str, type: str) -> list:
    """
    Parses a given string into a list of the obtained results with each
    result in dictionary form
    """
    # format the results in the required format
    data = BeautifulSoup(html_str, "html.parser")
    results = data.find_all("div", class_="result--url-above-snippet")
    formatted_data = []

    for result in results:
        tmp = {}
        body = result.find(class_="result__body")

        title = body.find(class_="result__title").find("a", class_="result__a").text
        breadcrumb_url = (
            body.find("div", class_="result__extras__url")
            .find("a", class_="result__url")
            .text
        )
        site_links = body.find_all("a", class_="sitelink--small__title")
        tmp["site_links"] = []

        for link in site_links:
            link_details = {}
            link_details["name"] = link.text.replace("\xa0", " ")
            link_details["url"] = link.attrs["href"]
            tmp["site_links"].append(link_details)

        # remove links from description
        long_description = body.find("div", class_="result__snippet")
        for child in long_description.find_all("div"):
            child.decompose()
        short_description = long_description.text

        tmp["title"] = title.replace("\xa0", " ")
        tmp["breadcrumb_url"] = breadcrumb_url.replace("\xa0", " ")
        tmp["description"] = short_description.replace("\xa0", " ")

        formatted_data.append(tmp)

    return formatted_data


def test_parser(comparision_data: list):
    test_data = os.path.dirname(os.path.realpath(__file__)) + "/test_data.html"
    with open(test_data) as test_data:
        contents = test_data.read()

    parsed_data = parse_response(contents, "text")

    # for debugging
    # for i in range(len(parsed_data)):
    #     p = parsed_data[i]
    #     e = expected[i]
    #     for k in p.keys():
    #         if p[k] != e[k]:
    #             print("parsed_data[{}] != expected[{}], index={}".format(k, k, i))
    #         else:
    #             print("parsed_data[{}] == expected[{}], index={}".format(k, k, i))
    #     print()

    print("Parsing data = ", end="")
    print("Success") if parsed_data == comparision_data else print("Failed")


def format_data(the_data: list, type: str = "plain_text") -> str:
    """
    Formats string obtained as response in the required

    Accepted formats are: xml, plain text and YAML

    If no format is provided, the default format is plain text
    """
    type = type.lower()
    if type not in ["xml", "plain_text", "yaml"]:
        raise ValueError(
            "Invalid format type {}. Allowed types are xml, plain_text and yaml",
            type,
        )

    if type == "plain_text":
        return format_plain_text(the_data)
    elif type == "xml":
        return format_xml(the_data)
    elif type == "yaml":
        return format_yaml(the_data)


def format_plain_text(the_data: list) -> str:
    all_results = ""

    result_skeleton = '"title": "{title}";\n"breadcrumb_url": "{bcrumb_url}";\n"description": "{desc}";\n"site_links":{site_links}\n;;\n'
    site_link_skeleton = '"name": "{name}", "url": "{url}";'

    for result in the_data:
        tmp_site_links = "\n"
        for link in result["site_links"]:
            current_link = site_link_skeleton.format(name=link["name"], url=link["url"])
            tmp_site_links += current_link + "\n"
        tmp_site_links = tmp_site_links.rstrip()

        #  fill in the skeleton
        tmp_placeholder = result_skeleton.format(
            title=result["title"],
            bcrumb_url=result["breadcrumb_url"],
            desc=result["description"],
            site_links=tmp_site_links,
        )
        all_results += tmp_placeholder + "\n"
    all_results = all_results.strip()
    all_results += "\n"

    return all_results


def format_xml(data: list):
    all_results = '<?xml version="1.0" encoding="UTF-8"?>\n<results>\n'
    result_shell = (
        "<result>\n<title>{title}</title>\n<breadcrumb_url>{breadcrumb_url}</breadcrumb_url>\n"
        "<description>{description}</description>\n<site_links>{site_links}</site_links>\n</result>"
    )
    site_link_shell = "<link><name>{name}</name><url>{url}</url></link>"

    for result in data:
        tmp_links = ""
        for link in result["site_links"]:
            tmp_link = site_link_shell.format(name=link["name"], url=link["url"])
            tmp_links += tmp_link + "\n"
        if tmp_links != "":
            tmp_links = "\n" + tmp_links

        tmp_result = result_shell.format(
            title=result["title"],
            breadcrumb_url=result["breadcrumb_url"],
            description=result["description"],
            site_links=tmp_links,
        )
        all_results += tmp_result + "\n"
    all_results += "</results>\n"
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
        # format links
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

        # format result
        # format description
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


def format_description(
    description: str, num_tabs: int, tab: str = "  ", line_len: int = 80
) -> str:
    """
    Formats a given result's description for consistency

    A tab consists of two spaces by default
    """
    # remove string splits
    tmp_description = description.replace("\n", " ")

    if len(tmp_description) < line_len:
        return tab * num_tabs + tmp_description

    segments = []
    # Count and split word at intervals
    # If we are going to split a word at current position, move back, look
    # for the beginning of the current word, and split string before the
    # word begins
    current = 0
    while current < len(tmp_description):
        next_breaking_point = current + line_len

        # ensure we don't break a word into two or carry over punctuation mark to the next line
        if not tmp_description[next_breaking_point].isspace():
            while (
                tmp_description[next_breaking_point].isalnum()
                or tmp_description[next_breaking_point] in string.punctuation
            ):
                next_breaking_point -= 1

        segments.append(tmp_description[current : next_breaking_point + 1])
        next_breaking_point += 1

        if next_breaking_point + line_len >= len(tmp_description):
            segments.append(tmp_description[next_breaking_point:])
            current = next_breaking_point + line_len
        else:
            current = next_breaking_point

    # remove whitespace from splits
    # remove multiple spaces
    # append tabs for formatting
    for i in range(len(segments)):
        segments[i] = segments[i].strip()
        segments[i] = re.sub(r"(\s)\s+", r"\g<1>", segments[i])
        segments[i] = (tab * num_tabs) + segments[i]

    formatted_string = "\n".join(segments)
    return formatted_string


def quote_str_with_special_chars(the_string: str) -> str:
    special_chars = ":{}[]&*#?|-><!%@`"
    for char in special_chars:
        if the_string.find(char) != -1:
            the_string = '"{}"'.format(the_string)
            break
    return the_string


def test_quote_str_with_special_chars():
    x = "&"
    z = "a:bc"

    x_format = quote_str_with_special_chars(x)
    z_format = quote_str_with_special_chars(z)
    print("Quoting special chars:")
    print("x = ", end="")
    print("Success") if x_format == '"&"' else print("Failed")
    print("z = ", end="")
    print("Success") if z_format == '"a:bc"' else print("Failed")


def test_format_description():
    description = (
        "Our father who art in heaven,\n"
        "Hallowed be thy name, thy kingdom come, thy will be done on earth as it is in heaven, give us this day\n"
        "our daily bread."
    )
    tab = "  "
    tab_size = 4
    expected = (
        "{tab_4}Our father who art in heaven, Hallowed be thy name, thy kingdom come, thy will\n"
        "{tab_4}be done on earth as it is in heaven, give us this day our daily bread."
    )

    expected = expected.format(tab_4=tab * tab_size)

    actual = format_description(description, tab_size, tab)

    a = format_description("", 2, tab)
    b = format_description("a", 1, tab)

    expected_a = tab * 2
    expected_b = tab * 1 + "a"

    print("Description formatting:")
    print("1 = ", end="")
    print("Success") if expected == actual else print("Failed")

    print("2 = ", end="")
    print("Success") if expected_a == a else print("Failed")

    print("3 = ", end="")
    print("Success") if expected_b == b else print("Failed")


def test_error_on_invalid_type():
    print("Exception thrown on invalid argument = ", end="")
    try:
        format_data([], "html")
    except ValueError:
        print("Success")
    else:
        print("Failed")


def test_txt_formatting(data: list):
    with open(
        os.path.dirname(os.path.abspath(__file__)) + "/formatted_data_plain_text"
    ) as txt_format:
        expected = txt_format.read()

    actual = format_plain_text(data)

    print("Text formatting = ", end="")
    print("Success") if expected == actual else print("Failed")


def test_xml_formatting(data: list):
    with open(
        os.path.dirname(os.path.abspath(__file__)) + "/formatted_data_xml"
    ) as xml_format:
        expected = xml_format.read()
    actual = format_xml(data)
    print("XML formatting = ", end="")
    print("Success") if actual == expected else print("Failed")


def test_yaml_formatting(data: list):
    actual = format_yaml(data)
    with open(
        os.path.dirname(os.path.abspath(__file__)) + "/formatted_data_yaml"
    ) as yaml_format:
        expected = yaml_format.read()

    print("YAML formatting = ", end="")
    print("Success") if actual == expected else print("Failed")


# test_parser(expected)
# test_error_on_invalid_type()
# test_txt_formatting(expected)
# test_xml_formatting(expected)
# test_yaml_formatting(expected)
# test_format_description()
# test_quote_str_with_special_chars()
