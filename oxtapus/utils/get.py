import requests

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
}


def get(url, timeout=(1, 3), verify=False):
    return requests.get(url, headers=headers, timeout=timeout, verify=verify)
