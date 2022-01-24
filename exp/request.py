import requests

r = requests.get('http://www.duckduckgo.com?q=news')

# print(r.status_code)
# print(r.headers)
print(type(r.headers))

print(r.text)
