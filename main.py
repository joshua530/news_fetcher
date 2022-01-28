# put everything together

from get_response import get, parse_response
import format_response

keywords = "fruits", "tropical", "sweet", "yellow", "or", "red"
response_txt = get(keywords)
parsed_response = parse_response(response_txt)

# xml
xml = format_response.format_xml(parsed_response)
# plain text
plain_text = format_response.format_plain_text(parsed_response)
# yaml
yaml = format_response.format_plain_text(parsed_response)

with open("xml_out", "w") as file:
    file.write(xml)
with open("text_out", "w") as file:
    file.write(plain_text)
with open("yaml_out", "w") as file:
    file.write(yaml)
