"""Minimal, provider-independent multi-asset screener."""
import pandas as pd

TYPES = {"stock", "etf", "fund", "crypto", "bond", "other"}
ELIGIBILITY = {"verified", "unverified", "ineligible"}


def load_assets(path):
    assets = pd.read_csv(path, dtype=str).fillna("")
    required = {"asset_id", "name", "asset_type", "ticker", "isin", "eligibility", "verified_at", "source"}
    if missing := required - set(assets.columns):
        raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")
    if assets["asset_id"].duplicated().any() or (assets["asset_id"] == "").any():
        raise ValueError("Each asset requires a unique nonempty asset_id (prefer ISIN where available).")
    if not assets["asset_type"].isin(TYPES).all():
        raise ValueError("Unknown asset_type")
    if not assets["eligibility"].isin(ELIGIBILITY).all():
        raise ValueError("Unknown eligibility")
    return assets


def rank_assets(assets, prices):
    """Rank by trailing 30-day momentum, only if 31+ daily observations exist.

    A demonstration ranking, not investment advice or a validated strategy.
    """
    result = assets.copy()
    result["return_30d_pct"] = float("nan")
    if prices.empty:
        return result
    required = {"asset_id", "date", "close_gbp"}
    if not required.issubset(prices.columns):
        raise ValueError("Prices require asset_id,date,close_gbp")
    p = prices.copy()
    p["date"] = pd.to_datetime(p["date"], errors="coerce")
    p["close_gbp"] = pd.to_numeric(p["close_gbp"], errors="coerce")
    p = p.dropna(subset=["date", "close_gbp"])
    p = p[p["close_gbp"] > 0].sort_values("date").drop_duplicates(["asset_id", "date"], keep="last")
    scores = {}
    for asset_id, g in p.groupby("asset_id"):
        if len(g) >= 31:
            # observation-based trailing return; dates may not be consecutive
            scores[asset_id] = (g.iloc[-1]["close_gbp"] / g.iloc[-31]["close_gbp"] - 1) * 100
    result["return_30d_pct"] = result["asset_id"].map(scores)
    return result.sort_values("return_30d_pct", ascending=False, na_position="last")
