# from request import get
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
            link_details["name"] = link.text.replace(u"\xa0", u" ")
            link_details["url"] = link.attrs["href"]
            tmp["site_links"].append(link_details)

        # remove links from description
        long_description = body.find("div", class_="result__snippet")
        for child in long_description.find_all("div"):
            child.decompose()
        short_description = long_description.text

        tmp["title"] = title.replace(u"\xa0", u" ")
        tmp["breadcrumb_url"] = breadcrumb_url.replace(u"\xa0", u" ")
        tmp["description"] = short_description.replace(u"\xa0", u" ")

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
    """
    if type.lower() not in ["xml", "plain_text", "yaml"]:
        raise ValueError(
            "Invalid format type {}. Allowed types are xml, plain_text and yaml",
            type,
        )

    if type == "plain_text":
        return format_plain_text(the_data)


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

    actual = format_data(data)

    print("Text formatting = ", end="")
    print("Success") if expected == actual else print("Failed")


# test_parser(expected)
# test_error_on_invalid_type()
# test_txt_formatting(expected)
