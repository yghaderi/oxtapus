# TSETMC public API inventory

This inventory was captured from the official public
[`MarketOverall`](https://tsetmc.com/MarketOverall) and instrument-detail interfaces on
2026-08-31. It combines browser-observed network traffic with route families extracted from
the exact JavaScript application bundle loaded by that browser session.

It is an inventory, not an assertion that every route is stable or supported by Oxtapus:

- **verified** — live payload, envelope, semantics, negative cases, and schema fingerprint
  are recorded in `endpoint_catalog.toml`; the route may be public if its transformer and
  tests are complete;
- **observed** — the official UI issued the request during this inspection;
- **discovered** — the route family exists in the official public bundle but was not called
  or probed during this inspection.

No authenticated, administrative, private, or non-public system was scanned. The crawl was
bounded to routes exposed by the public website and did not bulk-download every instrument.

## Implemented and live-verified routes

| Dataset | Route | Status |
|---|---|---|
| instrument search | `Instrument/GetInstrumentSearch/{term}` | verified |
| instrument information | `Instrument/GetInstrumentInfo/{insCode}` | verified |
| instrument identity | `Instrument/GetInstrumentIdentity/{insCode}` | verified |
| daily prices | `ClosingPrice/GetClosingPriceDailyList/{insCode}/0` | verified |
| bulk market watch | `ClosingPrice/GetMarketWatch` | verified |
| board quote | `ClosingPrice/GetClosingPriceInfo/{insCode}` | verified |
| five-level order book | `BestLimits/{insCode}` | verified |
| investor activity | `ClientType/GetClientType/{insCode}/1/0` | verified |
| board-member disclosures | `Codal/GetStatementContentByInsCode/12/0/-1/{insCode}` | verified |
| option market watch | `Instrument/GetInstrumentOptionMarketWatch/0` | verified |
| index levels | `Index/GetIndexB1LastAll/All/1` | experimental |
| market overview | `MarketData/GetMarketOverview/1` | experimental |

## Complete route-family inventory

The 84 unique public route families found in the loaded application bundle are grouped
below. `observed` means at least one concrete request was seen in browser traffic; all other
entries are `discovered` unless the table above marks them `verified`.

### Best limits and order book

| Route family | Evidence |
|---|---|
| `BestLimits/` | verified, observed |
| `BestLimits/GetBestLimitsTop/` | discovered |
| `BestLimits/GetBestLimitsTopPower/` | discovered |

### Investor type

| Route family | Evidence |
|---|---|
| `ClientType/GetClientType/` | verified, observed |
| `ClientType/GetClientTypeHistory/` | observed |

### Prices, charts, market watch, and rankings

| Route family | Evidence |
|---|---|
| `ClosingPrice/GetChartData/` | discovered |
| `ClosingPrice/GetClosingPrice/` | discovered |
| `ClosingPrice/GetClosingPriceDaily/` | discovered |
| `ClosingPrice/GetClosingPriceDailyList/` | verified, observed |
| `ClosingPrice/GetClosingPriceDailyListCSV/` | discovered |
| `ClosingPrice/GetClosingPriceHistory/` | discovered |
| `ClosingPrice/GetClosingPriceInfo/` | verified, observed |
| `ClosingPrice/GetIndexCompany/` | discovered |
| `ClosingPrice/GetInstrumentCalendar/` | discovered |
| `ClosingPrice/GetMarketCap/` | discovered |
| `ClosingPrice/GetMarketMap` | discovered |
| `ClosingPrice/GetPriceAdjustByFlow/` | discovered |
| `ClosingPrice/GetPriceAdjustList/` | discovered |
| `ClosingPrice/GetRelatedCompany/` | observed |
| `ClosingPrice/GetTradeTop/` | observed |

Observed ranking variants included `MostVisited/1/7`, `StandardSalaf/7/9999`, and the
expired standard-Salaf view. Their selector semantics remain unverified.

### Codal disclosures and statement files

| Route family | Evidence |
|---|---|
| `Codal/GetAttachmentContentFileByTracingNoAndRowOrder/` | discovered |
| `Codal/GetCodalPublisherBySymbol/` | observed |
| `Codal/GetContentFileByTracingNo/` | discovered |
| `Codal/GetFileAttachmentByMainTableRowId/` | discovered |
| `Codal/GetFileAttachmentByTracingNo/` | discovered |
| `Codal/GetPreparedData/` | observed |
| `Codal/GetPreparedDataByInsCode/` | observed |
| `Codal/GetStatementContentByInsCode/` | verified, observed |

Observed statement selector combinations were `12/0/-1` for board members, `13/0/-1`,
`6/6/0`, `6/6/1`, `6/6/2`, and `6/8/-1`. Only the board-member combination is enabled.

### Energy exchange

| Route family | Evidence |
|---|---|
| `Energy/GetAuctionById/` | discovered |
| `Energy/GetAuctionOrderById/` | discovered |
| `Energy/GetAuctionOverview/` | observed |
| `Energy/GetAuctionTradeById/` | discovered |
| `Energy/GetGetAuctionListItemByType/` | observed |
| `Energy/GetInstrumentTradeByAuctionId/` | discovered |
| `Energy/GetPowerOverview/` | discovered |

The public energy page requested auction-list types `ready`, `active`, `mazad`, and `ended`.

### Funds

| Route family | Evidence |
|---|---|
| `Fund/GetETFByInsCode/` | discovered |
| `Fund/GetFundInDetail/` | discovered |
| `Fund/GetFunds/` | observed |

### Indexes

| Route family | Evidence |
|---|---|
| `Index/GetIndexB1LastAll/` | verified, observed |
| `Index/GetIndexB1LastDay/` | discovered |
| `Index/GetIndexB2History/` | discovered |
| `Index/GetInstEffect/` | observed |

### Instruments and derivatives

| Route family | Evidence |
|---|---|
| `Instrument/GetInstrumentChartSymbolSearch/` | discovered |
| `Instrument/GetInstrumentEnergyFutureByInsCode/` | discovered |
| `Instrument/GetInstrumentFutureByCIsin/` | discovered |
| `Instrument/GetInstrumentHistory/` | discovered |
| `Instrument/GetInstrumentIdentity/` | verified, observed |
| `Instrument/GetInstrumentInfo/` | verified, observed |
| `Instrument/GetInstrumentOptionByInstrumentID/` | discovered |
| `Instrument/GetInstrumentOptionMarketWatch/` | verified |
| `Instrument/GetInstrumentOptionMarketWatchCSV/` | discovered |
| `Instrument/GetInstrumentSearch/` | verified |
| `Instrument/GetInstrumentShareChange/` | discovered |
| `Instrument/GetInstrumentShareChangeByFlow/` | discovered |

### Learning content

| Route family | Evidence |
|---|---|
| `Learning/GetLearningTopics` | discovered |

### Market aggregates and instrument state

| Route family | Evidence |
|---|---|
| `MarketData/GetContractBreakDownByFlow/` | discovered |
| `MarketData/GetInstrumentState/` | discovered |
| `MarketData/GetInstrumentStateAll/` | observed |
| `MarketData/GetInstrumentStateTop/` | observed |
| `MarketData/GetInstrumentStatistic/` | observed |
| `MarketData/GetMarketOverview/` | verified, observed |
| `MarketData/GetMarketValueByFlow/` | discovered |
| `MarketData/GetSectorTop/` | discovered |
| `MarketData/GetSectorsSummary` | discovered |
| `MarketData/GetStaticThreshold/` | discovered |

### Messages

| Route family | Evidence |
|---|---|
| `Msg/GetMsgByDevenAndLVal18AFC/` | discovered |
| `Msg/GetMsgByFlow/` | observed |
| `Msg/GetMsgByInsCode/` | observed |

### Shareholders

| Route family | Evidence |
|---|---|
| `Shareholder/` | discovered |
| `Shareholder/GetInstrumentShareHolderLast/` | observed |
| `Shareholder/GetShareHolderChanges/` | discovered |
| `Shareholder/GetShareHolderCompanyList/` | discovered |
| `Shareholder/GetShareHolderHistory/` | discovered |

### Static data

| Route family | Evidence |
|---|---|
| `StaticData/GetStaticContent/` | discovered |
| `StaticData/GetStaticData` | observed |
| `StaticData/GetTime` | observed |
| `StaticData/SetClickRecord` | observed |

`SetClickRecord` changes remote analytics state and is intentionally not a data-provider
capability.

### Supervision

| Route family | Evidence |
|---|---|
| `Supervision/GetSupervisionByInsCode/` | discovered |
| `Supervision/GetSupervisionListBySourceID/` | discovered |

### Trades

| Route family | Evidence |
|---|---|
| `Trade/GetTrade/` | observed |
| `Trade/GetTradeHistory/` | discovered |
| `Trade/GetTradeIntraDay/` | discovered |
| `Trade/GetTradeIntraDayCSV/` | discovered |
| `Trade/GetTradeVolume/` | discovered |

## UI requests observed outside the 84-family bundle list

The market landing page also issued `StaticData/GetStaticData`, `StaticData/GetTime`,
`MarketData/GetMarketOverview/1`, selected-index requests, instrument-effect rankings, and
most-visited rankings for market flows 1 and 2. Category tabs additionally issued
`Energy/GetAuctionOverview/0`, `Codal/GetPreparedData/100`, `Fund/GetFunds/6`, and commodity
ranking requests. These are captured above under their route families.

## Maintenance rule

On every TSETMC bundle change, regenerate the family list, diff it against this inventory,
and promote a route to the endpoint catalog only after live semantic verification, sanitized
fixtures, deterministic transforms, schema-drift reporting, and synchronous/asynchronous
contract tests are all present.
