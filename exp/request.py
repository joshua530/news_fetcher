import requests
from typing import Union


def get(keywords: Union[list, tuple]) -> str:
    if type(keywords).__name__ != "list" and type(keywords).__name__ != "tuple":
        raise TypeError("Invalid keywords type. Only a tuple or list should be used")

    search_query = "+".join(keywords)
    url = "https://www.duckduckgo.com?q={}&t=h_".format(search_query)

    req = requests.get(
        url, headers={"User-agent": "py-bot", "Accept-encoding": "gzip, deflate, br"}
    )
    response_text = req.text
    return response_text
