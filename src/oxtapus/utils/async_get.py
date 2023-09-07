import time
import aiohttp
import asyncio
from functools import wraps

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
}


def concurrency_limit_decorator(limit=3, retry_limit=5):
    sem = asyncio.Semaphore(limit)

    def executor(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with sem:
                retries = 0
                while retry_limit > retries:
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        retries += 1
                        time.sleep(retries)
                        if retries == retry_limit:
                            print(e)

        return wrapper

    return executor


@concurrency_limit_decorator(10, 5)
async def async_get(url, timeout=3, response_: str = "json"):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url=url,
            headers=headers,
            timeout=timeout,
        ) as response:
            if response_ == "json":
                return await response.json()
            return await response.text()
