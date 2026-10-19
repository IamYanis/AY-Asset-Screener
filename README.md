# A-Y Asset Screener — V0.2

A small Streamlit tool for comparing assets for the UMushroom UK Investment Competition 2026. Three application modules: `data.py` (inputs/provider), `screener.py` (four calculations), `app.py` (dashboard). No score, forecasts or trading recommendations.

## Run

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

On startup, the app loads the bundled `data/assets.csv` research watchlist and automatically requests Yahoo Finance history. No upload is required. The first load needs internet and may take a minute or more because retrieval is sequential. If the provider fails, the watchlist still appears with blank indicators and warnings. Upload an asset CSV to replace the watchlist, or upload a price CSV and select CSV to use your own history. Yahoo Finance is the default even when a price CSV is uploaded. You can also change the price-source selector manually. Filter by class and eligibility, choose an indicator and sort direction, or click table headers. Missing metrics sort last. Export the filtered table as CSV. The app works with CSV alone, without network access.

## Starter research watchlist

`data/assets.csv` contains 36 illustrative instruments: 16 stocks, 12 ETFs, four mutual funds and four cryptocurrencies. It spans US, UK, Japanese and Swiss company listings and sectors including technology, financials, healthcare, energy, consumer goods and industrials. ETFs cover global/developed/emerging equities, small caps, clean energy, bonds, property and gold exposure. The funds illustrate equity and bond fund histories; crypto symbols use USD pairs.

**Every starter asset is `unverified`. This is a research watchlist, not a list of confirmed UMushroom competition-eligible assets, and not a recommendation.** Some instruments, including US mutual fund share classes and US ETFs, may be unavailable to UK investors or in the competition. Asset diversity and Yahoo coverage do not establish eligibility. ISINs and verification dates are intentionally blank rather than guessed.

Each CSV row links to its exact [Yahoo quote](https://finance.yahoo.com/) in `source` and maps explicitly through `yahoo_ticker`. These links document instrument/provider provenance, not competition eligibility evidence. Fund share classes include [VFIAX](https://finance.yahoo.com/quote/VFIAX/), [VBTLX](https://finance.yahoo.com/quote/VBTLX/), [VWIGX](https://finance.yahoo.com/quote/VWIGX/) and [VSMAX](https://finance.yahoo.com/quote/VSMAX/). Edit the CSV to change the starter list. The app resolves its path relative to `app.py`, independent of the launch directory.

Yahoo history is cached for one hour for each imported universe, including errors for individual missing assets in a partial result, so filtering and sorting do not repeat successful downloads. Completely empty retrievals raise a visible error and are not cached; the next rerun retries them. **Refresh market data** clears the current universe's cached result and retrieves it again. The selected price source and number of Yahoo observations returned are shown above the table. CSV mode does not retrieve Yahoo data; if no price file is uploaded, the dashboard and export explicitly say so. Yahoo calls request raised provider exceptions rather than terminal-only logging; errors include the asset, symbol, exception type and message. The last retrieval attempt is shown in UTC and stays unchanged on cache hits; it is not a guarantee of successful or current prices. Each row's `price_date` shows the latest usable market observation. Partial failures retain successful histories; missing/invalid/stale histories have blank metrics and warnings or a `data_status` explanation. There is no saved offline market snapshot: without network, use the existing CSV price import.

## Eligibility and asset CSV

See [eligibility research and official sources](ELIGIBILITY_RESEARCH.md). A complete official eligible universe has **not** been obtained. The public UK 2026 pages contain stale Swiss 2025 content. No class or instrument is assumed eligible merely because it is listed on UMushroom.

Required header (also downloadable in the app):

```csv
asset_id,name,asset_type,ticker,isin,eligibility,verified_at,source,yahoo_ticker
example-apple,Apple,stock,AAPL,,unverified,,,AAPL
example-bitcoin,Bitcoin,crypto,BTC,,unverified,,,BTC-USD
```

These are mapping examples, **not confirmed eligible investments**. `yahoo_ticker` is optional and must identify the exact exchange listing/share class; no ticker or ISIN guessing is performed. `asset_id` must be unique and nonempty; preserve leading zeroes. Accepted classes: `stock`, `etf`, `fund`, `crypto`, `bond`, `other`. Eligibility: `verified`, `unverified`, `ineligible`; blank becomes `unverified`. Verified rows require a source and a valid non-future verification date. They represent your confirmation in the UK competition, not a check performed by this tool. Names and identifiers are supplied by the CSV.

## Prices

Upload daily observations with `asset_id,date,close,currency`; dates use ISO format and prices must be finite and positive. Legacy V0.1 `asset_id,date,close_gbp` is also accepted as GBP. Match asset IDs exactly. Use one consistent currency and adjustment basis per asset; `GBp` (pence) and `GBP` are different quote units. Missing/mixed currencies or duplicate dates block that asset's metrics. Invalid dates/prices and future observations are discarded; prices are never filled. `data_status` explains unavailable results, and `price_date` identifies the latest usable observation. Prices older than seven calendar days block all metrics.

Optional Yahoo retrieval uses [yfinance](https://github.com/ranaroussi/yfinance) and its [history API](https://ranaroussi.github.io/yfinance/reference/api/yfinance.Ticker.history.html), the only added direct dependency. It requests two years of daily adjusted prices and provider quote currency, one explicit `yahoo_ticker` per asset, with a 15-second history request timeout. Histories are cached for one hour; Refresh market data clears the current universe's cache. CSV and Yahoo are separate sources and never merged. Missing symbols, unsupported funds, provider errors or rate limits produce warnings and blank results. Yahoo access is unofficial and intended for personal research under the provider's applicable terms; there is no service guarantee. Use a permitted CSV if unavailable.

## Exactly four indicators

All are percentages, measured to each asset's own latest observation (shown in the table):

- **6-month / 12-month return:** `(last / baseline - 1) × 100`. Baseline is the last observation on or before the calendar-month anniversary, at most seven days earlier.
- **Annualised volatility:** sample standard deviation of daily simple returns in the trailing 12-month window, multiplied by `sqrt(252)` (or `sqrt(365)` for crypto) and 100.
- **Maximum drawdown:** minimum of `(price / running peak - 1) × 100` over that same 12-month window. A loss is negative; zero is valid for a series that never declines.

Each window requires at least 80% of expected daily observations (101/202 for six/twelve months of non-crypto, 146/292 for crypto), an anniversary baseline and no gap exceeding seven calendar days. The window includes that baseline. Sparse/weekly/monthly data and recent listings may therefore have blank metrics. Risk metrics require a complete qualifying 12-month window even when the 6-month return is available. Invalid observations are removed before these checks; remaining small gaps are not filled, so their multi-day returns can affect daily volatility. This is a conservative, simple screen rather than a market-calendar completeness check.

## Checks

```bash
python -m unittest discover -s tests -v
```

Tests use standard-library unittest, pandas and Streamlit's built-in AppTest; no test framework dependency. Synthetic fixtures test calculations and missing-data behavior, default watchlist loading, cached reruns, refresh, provider errors propagating through retrieval into the dashboard, retry after an empty failure, explicit CSV-without-upload status and the existing upload/filter/sort/export flow. Tests mock provider retrieval and do not need internet.

## Remaining limitations

No verified bulk universe, automatic eligibility validation, FX conversion, exchange calendars, database or scraping. Confirm current competition rules and exact share classes with organisers. Comparisons are in each asset's quote currency, **not GBP investor returns**; currency moves and differing observation dates may change relative outcomes. Yahoo adjustments may incorporate distributions/splits; CSV basis is the user's responsibility. Neither is guaranteed to reproduce UMushroom execution, fees, dividends or valuation. Historical performance does not predict returns. Keep the universe small: retrieval is sequential and has no retry infrastructure.

## Institutional research — Stage 1

The separate offline [research pipeline](research/README.md) ingests the five local institutional snapshots and writes source-specific datasets plus a [data-quality report](research/data_quality_report.md). It adds no dashboard features, scores or recommendations. Optional PDF/Excel dependencies are in `research/requirements.txt`; downloaded and processed research files stay out of Git.
