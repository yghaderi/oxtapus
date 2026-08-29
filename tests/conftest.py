"""Sanitized provider fixtures shared by offline tests."""

from __future__ import annotations

import json
import threading
from datetime import UTC, datetime

import pytest

from oxtapus.progress.reporter import ProgressReporter
from oxtapus.transport.base import RawResponse, TransportRequest


def payload_for(url: str) -> dict[str, object]:
    """Return a minimal sanitized envelope for a catalog-owned route."""

    if "GetInstrumentSearch" in url:
        return {
            "instrumentSearch": [
                {
                    "insCode": "46348559193224090",
                    "lVal30": "فولاد مبارکه اصفهان",
                    "lVal18AFC": "فولاد",
                    "flow": 1,
                    "cIsin": "IRO1FOLD0001",
                    "instrumentID": "IRO1FOLD0005",
                    "cgrValCot": "N1",
                    "lastDate": 1,
                    "flowTitle": "بورس",
                    "cgrValCotTitle": "بازار اول",
                }
            ]
        }
    if "GetInstrumentInfo" in url:
        return {
            "instrumentInfo": {
                "insCode": "46348559193224090",
                "lVal30": "فولاد مبارکه اصفهان",
                "lVal18AFC": "فولاد",
                "flow": 1,
                "cIsin": "IRO1FOLD0001",
                "instrumentID": "IRO1FOLD0005",
                "cgrValCot": "N1",
                "lastDate": 1,
                "flowTitle": "بورس",
                "cgrValCotTitle": "بازار اول",
                "sector": {"cSecVal": "27", "lSecVal": "فلزات اساسی"},
            }
        }
    if "GetClosingPriceDailyList" in url:
        return {
            "closingPriceDaily": [
                {
                    "insCode": "46348559193224090",
                    "dEven": 20250102,
                    "priceFirst": 4200,
                    "priceMax": 4300,
                    "priceMin": 4100,
                    "pClosing": 4250,
                    "pDrCotVal": None,
                    "priceYesterday": 4180,
                    "priceChange": 70,
                    "zTotTran": 100,
                    "qTotTran5J": 200000,
                    "qTotCap": 850000000,
                }
            ]
        }
    if "GetMarketWatch" in url:
        return {
            "marketwatch": [
                {
                    "insCode": "46348559193224090",
                    "insID": "IRO1FOLD0005",
                    "lva": "فولاد",
                    "lvc": "فولاد مبارکه اصفهان",
                    "pf": 4200,
                    "pmx": 4300,
                    "pmn": 4100,
                    "pdv": 4270,
                    "pcl": 4250,
                    "py": 4180,
                    "pc": 70,
                    "ztt": 100,
                    "qtj": 200000,
                    "qtc": 850000000,
                    "hEven": 123045,
                }
            ]
        }
    if "GetInstrumentOptionMarketWatch" in url:
        return {
            "instrumentOptMarketWatch": [
                {
                    "insCode_P": "111111",
                    "insCode_C": "222222",
                    "contractSize": 1000,
                    "uaInsCode": "46348559193224090",
                    "lVal18AFC_P": "طفولاد",
                    "lVal30_P": "اختیار فروش فولاد",
                    "lval30_UA": "فولاد",
                    "endDate": "20261221",
                    "strikePrice": 5000,
                    "lVal30_C": "اختیار خرید فولاد",
                    "lVal18AFC_C": "ضفولاد",
                    "pClosing_P": 90,
                    "pClosing_C": 110,
                }
            ]
        }
    raise AssertionError(f"Unexpected fixture URL: {url}")


class FakeSyncTransport:
    """Thread-safe offline transport implementing the public boundary."""

    def __init__(self) -> None:
        self.requests: list[TransportRequest] = []
        self.close_calls = 0
        self._lock = threading.Lock()

    def request(self, request: TransportRequest, *, reporter: ProgressReporter) -> RawResponse:
        with self._lock:
            self.requests.append(request)
        return response_for(request)

    def close(self) -> None:
        self.close_calls += 1


class FakeAsyncTransport:
    """Offline native async transport implementing the public boundary."""

    def __init__(self) -> None:
        self.requests: list[TransportRequest] = []
        self.close_calls = 0

    async def request(
        self, request: TransportRequest, *, reporter: ProgressReporter
    ) -> RawResponse:
        self.requests.append(request)
        return response_for(request)

    async def aclose(self) -> None:
        self.close_calls += 1


def response_for(request: TransportRequest) -> RawResponse:
    content = json.dumps(payload_for(request.url), ensure_ascii=False).encode()
    return RawResponse(
        request_id=f"request-{len(content)}",
        operation_id=request.operation_id,
        endpoint=request.endpoint,
        capability=request.capability,
        url=request.url,
        status_code=200,
        headers={"content-type": "application/json", "etag": "sanitized"},
        content=content,
        retrieved_at=datetime(2026, 8, 29, 12, 30, tzinfo=UTC),
        elapsed_seconds=0.01,
        retry_count=0,
    )


@pytest.fixture
def sync_transport() -> FakeSyncTransport:
    return FakeSyncTransport()


@pytest.fixture
def async_transport() -> FakeAsyncTransport:
    return FakeAsyncTransport()
