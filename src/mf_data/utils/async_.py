import time
import pandas as pd
import requests
import aiohttp
import asyncio

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
}


async def get(ins_code):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"http://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/{ins_code}/0",
            headers=headers,
            timeout=3,
        ) as response:
            print("Status:", response.status)
            html = await response.json()
            return pd.DataFrame(html["closingPriceDaily"])


async def main():
    await asyncio.gather(
        get("65883838195688438"),
        get("65883838195688438"),
        get("65883838195688438"),
        get("65883838195688438"),
    )


if __name__ == "__main__":
    start = time.perf_counter()
    a = asyncio.run(get("65883838195688438"))
    # asyncio.run(main())
    end = time.perf_counter()
    print(f"time: {end - start :.2f}s")
    print(a.head(1))
