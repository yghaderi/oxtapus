import requests

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Host": "tsd.cbi.ir",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
}


def headers_with_cookie(cookies):
    return {
        **headers,
        "Cookie": f"f5_cspm=1234; ASP.NET_SessionId={cookies.get('ASP.NET_SessionId')}; TS015252a9={cookies.get('TS015252a9')}",
    }


def get(url, rep_url, headers=headers, timeout=(2, 5)):
    session = requests.Session()
    response = session.get(url=url)
    hwc = headers_with_cookie(session.cookies.get_dict())
    response = session.get(url=url, headers=hwc)
    hwc = headers_with_cookie(session.cookies.get_dict())
    print(hwc)
    return session.get(url=rep_url, headers=hwc)
