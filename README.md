# A-Y Asset Screener — V0.1

A minimal multi-asset shortlist tool for the UMushroom UK Investment Competition.

## Start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

## Universe acquisition

1. Ask UMushroom for an official UK 2026 competition-eligible asset export/API with identifiers, asset classes and trading restrictions.
2. Check the competition's **Add Investments** interface for eligibility; preserve the verification date and source.
3. Import a CSV with `asset_id,name,asset_type,ticker,isin,eligibility,verified_at,source`.
4. Mark an asset `verified` ONLY after confirming it can be selected in the competition. Everything else defaults to `unverified` or `ineligible`.
5. Do not scrape private endpoints or assume that UMushroom's global platform catalogue equals the eligible competition universe.

Accepted classes: `stock`, `etf`, `fund`, `crypto`, `bond`, `other`.
Accepted eligibility statuses: `verified`, `unverified`, `ineligible`.
The asset_id should be stable (ISIN when appropriate); crypto and some other assets need alternative IDs.

## Price inputs

Optional CSV columns: `asset_id,date,close_gbp` (date in ISO format, strictly positive GBP price).
V0.1 sorts available assets by return between latest and 30 observations earlier. This is not a 30-calendar-day return, a predictive score, or a cross-asset recommendation. Assets without sufficient history remain unsorted.

## Not included yet

Bulk UMushroom integration, automatic market/FX data, risk metrics, asset-class-specific fundamentals, backtesting, portfolio optimisation or automated trading.

## Important

Published UMushroom FAQ text may refer to past Swiss contests and should not be assumed to establish rules for UK 2026. Confirm the current rulebook and eligibility conditions with the organisers.
