"""CSV inputs and optional Yahoo Finance history; no UMushroom scraping."""
import pandas as pd

TYPES = {"stock", "etf", "fund", "crypto", "bond", "other"}
ELIGIBILITY = {"verified", "unverified", "ineligible"}
ASSET_COLUMNS = "asset_id,name,asset_type,ticker,isin,eligibility,verified_at,source"
PRICE_COLUMNS = "asset_id,date,close,currency"


def load_assets(path):
    assets = pd.read_csv(path, dtype=str).fillna("")
    if missing := set(ASSET_COLUMNS.split(",")) - set(assets.columns):
        raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")
    assets = assets.apply(lambda column: column.str.strip())
    if assets.asset_id.duplicated().any() or assets.asset_id.eq("").any():
        raise ValueError("Each asset requires a unique nonempty asset_id.")
    if assets.name.eq("").any() or not assets.asset_type.isin(TYPES).all():
        raise ValueError("Supply an asset name and a supported asset_type.")
    assets.loc[assets.eligibility.eq(""), "eligibility"] = "unverified"
    if not assets.eligibility.isin(ELIGIBILITY).all():
        raise ValueError("Unknown eligibility status.")
    verified = assets.eligibility.eq("verified")
    dates = pd.to_datetime(assets.verified_at, errors="coerce", utc=True)
    if (verified & (assets.source.eq("") | dates.isna() | (dates > pd.Timestamp.now(tz="UTC")))).any():
        raise ValueError("Verified assets require a source and a valid, non-future verified_at date.")
    return assets


def load_prices(path):
    prices = pd.read_csv(path, dtype={"asset_id": str})
    if "close_gbp" in prices and "close" not in prices:
        prices = prices.rename(columns={"close_gbp": "close"})
        prices["currency"] = "GBP"
    if not set(PRICE_COLUMNS.split(",")).issubset(prices.columns):
        raise ValueError("Prices require asset_id,date,close,currency (or legacy close_gbp).")
    return prices


def fetch_prices(assets):
    """Explicit yahoo_ticker mapping avoids guessing ISINs or exchange listings."""
    import yfinance as yf

    frames, errors = [], []
    for _, asset in assets.iterrows():
        symbol = asset.get("yahoo_ticker", "")
        if not symbol:
            errors.append(f"{asset.asset_id}: no yahoo_ticker mapping; import prices instead.")
            continue
        try:
            ticker = yf.Ticker(symbol)
            history = ticker.history(period="2y", interval="1d", auto_adjust=True, timeout=15, raise_errors=True)
            if history.empty:
                raise ValueError("no history returned")
            currency = ticker.get_history_metadata().get("currency", "")
            if not currency:
                raise ValueError("provider did not report a quote currency")
            frames.append(pd.DataFrame({"asset_id": asset.asset_id,
                "date": history.index.tz_localize(None).normalize(),
                "close": history["Close"].to_numpy(), "currency": currency}))
        except Exception as exc:
            errors.append(f"{asset.asset_id} ({symbol}): {type(exc).__name__}: {exc}")
    return (pd.concat(frames, ignore_index=True) if frames else
            pd.DataFrame(columns=PRICE_COLUMNS.split(","))), errors
