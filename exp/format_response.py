from request import get

response = get(['news', 'latest', 'entertainment'])


def format_response(response_str: str, type: str):
    '''
    Formats string obtained as response in the required
    format:

    Accepted formats are: xml, plain text and YAML
    '''
