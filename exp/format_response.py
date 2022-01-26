# from request import get
from test_result import expected
import os

# response = get(['news', 'latest', 'entertainment'])


def parse_response(response_str: str, type: str) -> dict:
    '''
    Parses a given string into a list of the obtained results with each
    result in dictionary form
    '''
    # break down the text into a dictionary(results) of dictionaries(result)
    # the child dictionaries will contain info in the format
    # {
    #   title: <title>,
    #   breadcrumb_url: <breadcrumb url>,
    #   description: <result description(get rid of <b> tags)>,
    #   site_links: [
    #     {name: <site name>, url: <link url>}
    #   ]
    # }

    # format the results in the required format
    return {}

# Formats string obtained as response in the required
#     format:

#     Accepted formats are: xml, plain text and YAML


test_data = os.path.dirname(os.path.realpath(__file__)) + '/test_data.html'
with open(test_data) as test_data:
    contents = test_data.read()

parsed_data = parse_response(contents, 'text')

if parsed_data == expected:
    print('Yaaay')
else:
    print('Nah')
