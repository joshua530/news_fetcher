import requests

r = requests.get('http://www.duckduckgo.com?q=news&t=h_', headers={
    # 'Host': 'duckduckgo.com',
    # 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0',
    'User-Agent': 'py-bot',
    # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    # 'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    # 'Connection': 'keep-alive',
    # 'Upgrade-Insecure-Requests': '1',
    # 'Sec-Fetch-Dest': 'document',
    # 'Sec-Fetch-Mode': 'navigate',
    # 'Sec-Fetch-Site': 'none',
    # 'Sec-Fetch-User': '?1',
    # 'Referer': 'https://duckduckgo.com'
})

# print(r.status_code)
# print(r.headers)
# print(type(r.headers))

print(r.text)
