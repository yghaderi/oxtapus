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
                "eps": {
                    "epsValue": 512,
                    "estimatedEPS": "530",
                    "sectorPE": 6.2,
                    "psr": 1.4,
                },
                "staticThreshold": {"psGelStaMax": 4400, "psGelStaMin": 4000},
                "minWeek": 3900,
                "maxWeek": 4300,
                "minYear": 3200,
                "maxYear": 5100,
                "qTotTran5JAvg": 190000,
                "contractSize": 0,
                "underSupervision": 0,
                "zTitad": 800000000000,
                "baseVol": 1,
            }
        }
    if "GetInstrumentIdentity" in url:
        return {
            "instrumentIdentity": {
                "sector": {"cSecVal": "27", "lSecVal": "فلزات اساسی"},
                "subSector": {"cSoSecVal": 2710, "lSoSecVal": "تولید آهن و فولاد"},
                "cValMne": "FOLD1",
                "lVal18": "Foolad Mobarakeh",
                "cSocCSAC": "FOLD",
                "lSoc30": "فولاد مبارکه اصفهان",
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
    if "GetClosingPriceInfo" in url:
        return {
            "closingPriceInfo": {
                "instrumentState": {
                    "cEtaval": "A ",
                    "underSupervision": 0,
                    "cEtavalTitle": "مجاز",
                },
                "lastHEven": 123030,
                "finalLastDate": 20260831,
                "priceChange": 70,
                "priceMin": 4100,
                "priceMax": 4300,
                "priceYesterday": 4180,
                "priceFirst": 4200,
                "dEven": 20260831,
                "hEven": 123045,
                "pClosing": 4250,
                "pDrCotVal": 4270,
                "zTotTran": 100,
                "qTotTran5J": 200000,
                "qTotCap": 850000000,
            }
        }
    if "/api/BestLimits/" in url:
        return {
            "bestLimits": [
                {
                    "number": 1,
                    "qTitMeDem": 10000,
                    "zOrdMeDem": 4,
                    "pMeDem": 4260,
                    "pMeOf": 4270,
                    "zOrdMeOf": 3,
                    "qTitMeOf": 12000,
                    "title": None,
                    "insCode": None,
                },
                {
                    "number": 2,
                    "qTitMeDem": 8000,
                    "zOrdMeDem": 2,
                    "pMeDem": 4250,
                    "pMeOf": 4280,
                    "zOrdMeOf": 5,
                    "qTitMeOf": 16000,
                    "title": None,
                    "insCode": None,
                },
            ]
        }
    if "GetClientType" in url:
        return {
            "clientType": {
                "buy_I_Volume": 150000,
                "buy_N_Volume": 50000,
                "buy_DDD_Volume": 0,
                "buy_CountI": 90,
                "buy_CountN": 10,
                "buy_CountDDD": 0,
                "sell_I_Volume": 130000,
                "sell_N_Volume": 70000,
                "sell_CountI": 80,
                "sell_CountN": 20,
            }
        }
    if "GetStatementContentByInsCode/12/0/-1" in url:
        content = """<BoardMember>
          <AssemblyDate>1405/05/20</AssemblyDate>
          <BoardMembersSessionDate>1405/05/25</BoardMembersSessionDate>
          <BoardMembers><BoardMember>
            <MemberName>شرکت سرمایه گذاری نمونه</MemberName>
            <NationalCode_RegisterNumber>10101234567</NationalCode_RegisterNumber>
            <Designation>رئیس هیئت مدیره</Designation>
            <Charged>موظف</Charged>
            <EducationDegree>کارشناسی ارشد</EducationDegree>
            <Agent>علی نمونه</Agent>
            <AgentNationalCode>0012345678</AgentNationalCode>
          </BoardMember></BoardMembers>
          <DirectorManager>
            <DirectorManagerName>رضا نمونه</DirectorManagerName>
            <DirectorManagerNationalCode>0098765432</DirectorManagerNationalCode>
            <DirectorManagerEducationDegree>دکتری</DirectorManagerEducationDegree>
          </DirectorManager>
        </BoardMember>"""
        return {
            "statemetnContent": [
                {
                    "title": "معرفی اعضای هیئت مدیره",
                    "sentDateTime_Gregorian": "2026-08-11T12:10:00",
                    "publishDateTime_Gregorian": "2026-08-11T12:20:00",
                    "publishDateTime_DEven": 20260811,
                    "reportSubType": 0,
                    "pageID": 12345,
                    "content": content,
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
    if "summary-table-data" in url:
        return {
            "data": [
                [
                    "100,000",
                    "99,000",
                    "102,000",
                    "101,000",
                    '<span class="high" dir="ltr">1,000</span>',
                    '<span class="high" dir="ltr">1.00%</span>',
                    "2026/09/26",
                    "1405/07/04",
                ],
                [
                    "101,000",
                    "98,000",
                    "101,500",
                    "99,000",
                    '<span class="low" dir="ltr">2,000</span>',
                    '<span class="low" dir="ltr">1.98%</span>',
                    "2026/09/27",
                    "1405/07/05",
                ],
            ],
            "draw": 1,
            "recordsFiltered": 2,
            "recordsTotal": 2,
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
