import asyncio
import httpx
from tenacity import retry, wait_random, stop_after_delay
from requests import Session

__all__ = ["get", "async_requests"]

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
}


@retry(wait=wait_random(min=1, max=5), stop=stop_after_delay(90))
def get(
    url: str | list[str], response: str = "json", timeout=(1, 3), verify: bool = True
):
    with Session() as s:
        if not isinstance(url, list):
            url = [url]
        list_r = []
        for i in url:
            r = s.get(url=i, headers=headers, timeout=timeout, verify=verify)
            match response:
                case "json":
                    list_r.append(r.json())
                case "text":
                    list_r.append(r.text)
                case _:
                    list_r.append(r)
        return list_r


@retry(wait=wait_random(min=1, max=5), stop=stop_after_delay(90))
async def _async_requests(url: str, response: str, timeout, verify: bool):
    async with httpx.AsyncClient(verify=verify) as client:
        async with asyncio.Semaphore(3):
            r = await client.get(url=url, headers=headers, timeout=timeout)
            match response:
                case "json":
                    return r.json()
                case "text":
                    return r.text
                case _:
                    return r


def async_requests(
    url: str | list[str], response: str = "json", timeout=(1, 3), verify: bool = True
):
    if isinstance(url, list):
        task = [_async_requests(i, response, timeout, verify) for i in url]
    else:
        task = [_async_requests(url, response, timeout, verify)]

    async def main():
        return await asyncio.gather(*task)

    return asyncio.get_event_loop().run_until_complete(main())
