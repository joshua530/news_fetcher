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


test_parser(expected)
