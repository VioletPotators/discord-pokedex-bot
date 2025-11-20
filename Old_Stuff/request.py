import requests
response = requests.get(
    "https://ipv4.webshare.io/",
    proxies={
        "http": "socks5://qfkonkyp-rotate:t45l3o586kn3@p.webshare.io:80/",
        "https": "socks5://qfkonkyp-rotate:t45l3o586kn3@p.webshare.io:80/"
    }
).text
print(response)