from typing import Union
from bs4 import BeautifulSoup
import requests


def get(keywords: Union[list, tuple]) -> str:
    """
    response comes back in gibberish form.
    Not currently parsable in the way that the business logic
    is implemented
    """
    keywords_type = type(keywords).__name__
    if keywords_type != "list" and keywords_type != "tuple":
        raise TypeError("Only a tuple or list is allowed for the keywords")

    query = "https://duckduckgo.com/html/?q={}&t=h_&ia=web".format("+".join(keywords))
    response = requests.get(
        query,
        headers={
            "User-agent": "python-bot",
            "Accept-encoding": "gzip, deflate, br",
        },
    )

    return response.text


def parse_response(response: str) -> list:
    """
    Parses a given string into a list of results with each result being
    a dictionary
    """
    data = BeautifulSoup(response, "html.parser")

    all_results = data.find_all("div", class_="result--url-above-snippet")
    formatted_data = []

    for result in all_results:
        tmp_result = {}
        body = result.find(class_="result__body")
        site_links = body.find_all("a", class_="sitelink--small__title")

        title = result.find(class_="result__title").find("a", class_="result__a").text
        breadcrumb_url = (
            body.find("div", class_="result__extras__url")
            .find("a", class_="result__url")
            .text
        )

        tmp_result["site_links"] = []
        for link in site_links:
            tmp_link = {}
            tmp_link["url"] = link.text.replace("\xa0", " ")
            tmp_link["name"] = link.attrs["href"]
            tmp_result["site_links"].append(tmp_link)

        # remove links from description
        long_description = body.find("div", class_="result__snippet")
        for child in long_description.find_all("div"):
            child.decompose()
        result_description = long_description.text

        tmp_result["title"] = title.text.replace("\xa0", " ")
        tmp_result["breadcrumb_url"] = breadcrumb_url.replace("\xa0", " ")
        tmp_result["description"] = result_description.replace("\xa0", " ")

        formatted_data.append(tmp_result)
    return formatted_data
