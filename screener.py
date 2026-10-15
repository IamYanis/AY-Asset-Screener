"""Four historical indicators, with conservative daily-history requirements."""
import math
import pandas as pd

INDICATORS = ["return_6m_pct", "return_12m_pct", "volatility_pct", "max_drawdown_pct"]


def screen_assets(assets, prices, as_of=None):
    as_of = pd.Timestamp(as_of or pd.Timestamp.today()).normalize()
    result = assets.copy()
    for column in INDICATORS:
        result[column] = float("nan")
    result["currency"] = ""
    result["price_date"] = ""
    result["data_status"] = "No usable prices"
    if prices.empty:
        return result
    p = prices.copy()
    p["date"] = pd.to_datetime(p.date, errors="coerce", utc=True).dt.tz_localize(None).dt.normalize()
    p["close"] = pd.to_numeric(p.close, errors="coerce")
    p = p[p.date.le(as_of) & p.close.gt(0) & p.close.lt(float("inf"))]
    p = p.dropna(subset=["date", "close"]).sort_values("date")
    for index, asset in result.iterrows():
        g = p[p.asset_id.eq(asset.asset_id)].copy()
        if g.empty:
            continue
        currencies = g.currency.fillna("").astype(str).str.strip().unique()
        if len(currencies) != 1 or not currencies[0]:
            result.at[index, "data_status"] = "Missing or mixed currencies"
            continue
        result.at[index, "currency"] = currencies[0]
        if g.date.duplicated().any():
            result.at[index, "data_status"] = "Duplicate price dates; resolve before calculating"
            continue
        s = g.set_index("date").close
        end = s.index[-1]
        result.at[index, "price_date"] = end.date().isoformat()
        if (as_of - end).days > 7:
            result.at[index, "data_status"] = "Stale prices (over 7 days old)"
            continue
        annual_days = 365 if asset.asset_type == "crypto" else 252
        notes = []
        for months in (6, 12):
            target = end - pd.DateOffset(months=months)
            baseline = s.loc[:target]
            window = s.loc[baseline.index[-1]:] if not baseline.empty else s.iloc[:0]
            minimum = math.ceil(annual_days * months / 12 * 0.8)
            usable = (not baseline.empty and (target - baseline.index[-1]).days <= 7
                      and len(window) >= minimum
                      and window.index.to_series().diff().dt.days.max() <= 7)
            if not usable:
                notes.append(f"Insufficient/gapped {months}m history")
                continue
            result.at[index, f"return_{months}m_pct"] = (s.iloc[-1] / window.iloc[0] - 1) * 100
            if months == 12:
                returns = window.pct_change(fill_method=None).dropna()
                result.at[index, "volatility_pct"] = returns.std(ddof=1) * math.sqrt(annual_days) * 100
                result.at[index, "max_drawdown_pct"] = (window / window.cummax() - 1).min() * 100
        result.at[index, "data_status"] = "; ".join(notes) or "OK"
    return result
