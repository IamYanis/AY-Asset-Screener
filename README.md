# A-Y Asset Screener — V0.2

A small Streamlit tool for comparing assets for the UMushroom UK Investment Competition 2026. Three application modules: `data.py` (inputs/provider), `screener.py` (four calculations), `app.py` (dashboard). No score, forecasts or trading recommendations.

## Run

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Import an asset CSV, then upload prices or select Yahoo Finance. Filter by class and eligibility, choose an indicator and sort direction, or click table headers. Missing metrics sort last. Export the filtered table as CSV. The app works with CSV alone, without network access.

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

Optional Yahoo retrieval uses [yfinance](https://github.com/ranaroussi/yfinance) and its [history API](https://ranaroussi.github.io/yfinance/reference/api/yfinance.Ticker.history.html), the only added direct dependency. It requests two years of daily adjusted prices and provider quote currency, one explicit `yahoo_ticker` per asset, with a 15-second history request timeout. Histories are cached for one hour; Refresh clears that cache. CSV and Yahoo are separate sources and never merged. Missing symbols, unsupported funds, provider errors or rate limits produce warnings and blank results. Yahoo access is unofficial and intended for personal research under the provider's applicable terms; there is no service guarantee. Use a permitted CSV if unavailable.

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

Tests use standard-library unittest, pandas and Streamlit's built-in AppTest; no test framework dependency. Synthetic fixtures test calculations and missing-data behavior; provider tests do not need internet.

## Remaining limitations

No verified bulk universe, automatic eligibility validation, FX conversion, exchange calendars, database or scraping. Confirm current competition rules and exact share classes with organisers. Comparisons are in each asset's quote currency, **not GBP investor returns**; currency moves and differing observation dates may change relative outcomes. Yahoo adjustments may incorporate distributions/splits; CSV basis is the user's responsibility. Neither is guaranteed to reproduce UMushroom execution, fees, dividends or valuation. Historical performance does not predict returns. Keep the universe small: retrieval is sequential and has no retry infrastructure.
