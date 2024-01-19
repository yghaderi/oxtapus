from typing import List
import requests
from tenacity import retry, wait_random, stop_after_delay


headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
}


def request(url: str | List[str], response: str = "json", timeout=(1, 10)):
    with requests.Session() as s:
        if isinstance(url, list):
            list_r = []
            for i in url:
                r = s.get(url=i, headers=headers, timeout=timeout)
                match response:
                    case "json":
                        list_r.append(r.json())
                    case "text":
                        list_r.append(r.text)
                    case _:
                        list_r.append(r)
            return list_r

        r = s.get(url=url, headers=headers, timeout=timeout)
        match response:
            case "json":
                return [r.json()]
            case "text":
                return [r.text]
            case _:
                return [r]
