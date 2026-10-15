from pathlib import Path
import pandas as pd
import streamlit as st
from data import ASSET_COLUMNS, PRICE_COLUMNS, TYPES, load_assets, load_prices, fetch_prices
from screener import INDICATORS, screen_assets

st.set_page_config(page_title="A-Y Asset Screener", layout="wide")
st.title("A-Y Asset Screener — V0.2")
st.caption("Historical comparisons. Eligibility must be confirmed for the UK 2026 competition.")
st.info("No complete official eligible universe has been confirmed. 'verified' means your CSV records competition-specific evidence; listing on UMushroom alone is insufficient.")
st.info("The bundled starter watchlist is for research only. Every starter asset is unverified for competition eligibility. Upload an asset CSV to replace it.")
asset_file = st.file_uploader("Import asset universe CSV", type="csv")
price_file = st.file_uploader("Import price histories CSV (optional)", type="csv")
st.download_button("Download blank asset CSV", ASSET_COLUMNS + ",yahoo_ticker\n", "assets_template.csv")
st.download_button("Download blank price CSV", PRICE_COLUMNS + "\n", "prices_template.csv")
mode = st.radio("Price source", ["CSV", "Yahoo Finance"], index=1, horizontal=True)
st.caption("Yahoo mode requires an explicit yahoo_ticker column. CSV and Yahoo histories are never mixed.")

@st.cache_data(ttl=3600, show_spinner="Retrieving daily prices…")
def yahoo_history(assets):
    prices, errors = fetch_prices(assets)
    if prices.empty:
        detail = "\n".join(errors) or "The provider returned an empty history without an error message."
        # Streamlit does not cache exceptions, so a temporary outage can recover.
        raise ValueError("Yahoo Finance retrieval failed; no price observations returned.\n" + detail)
    return prices, errors, pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d %H:%M:%S UTC")

try:
    assets = load_assets(asset_file if asset_file is not None else Path(__file__).resolve().parent / "data" / "assets.csv")
    st.caption("Asset universe: " + ("uploaded CSV" if asset_file is not None else "bundled research watchlist (data/assets.csv)"))
    st.caption(f"Selected price source: {mode}")
    prices = pd.DataFrame()
    if mode == "Yahoo Finance":
        if st.button("Refresh market data"):
            yahoo_history.clear(assets)
        try:
            prices, errors, retrieved_at = yahoo_history(assets)
        except ValueError as exc:
            st.caption("Last retrieval attempt: " + pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d %H:%M:%S UTC") + " (failed; not cached)")
            st.error(str(exc))
            st.info("No empty result was cached. Use Refresh market data to retry, check network access to Yahoo Finance, or upload a price CSV and select CSV.")
        else:
            st.caption(f"Last retrieval attempt: {retrieved_at}. Cached for one hour; price_date shows each asset's latest observation.")
            st.caption(f"Yahoo returned {len(prices)} price observations for {prices.asset_id.nunique()} of {len(assets)} assets.")
            for error in errors:
                st.warning(error)
    elif price_file is not None:
        prices = load_prices(price_file)
    result = screen_assets(assets, prices)
    if mode == "Yahoo Finance" and prices.empty:
        result["data_status"] = "Yahoo retrieval failed; see dashboard errors"
    elif mode == "CSV" and price_file is None:
        st.error("CSV is selected but no price CSV is uploaded. Yahoo retrieval was not attempted. Select Yahoo Finance to retrieve market data.")
        result["data_status"] = "CSV selected; no price file uploaded"
    elif result.data_status.eq("No usable prices").all() and not result.empty:
        st.error(f"{mode} supplied no usable prices for the selected asset IDs. Check price dates, positive finite closes and matching asset_id values.")
except (ValueError, OSError, pd.errors.ParserError) as exc:
    st.error(str(exc))
    st.stop()

status = st.multiselect("Eligibility", ["verified", "unverified", "ineligible"], default=["verified", "unverified"])
classes = st.multiselect("Asset class", sorted(TYPES), default=sorted(TYPES))
result = result[result.eligibility.isin(status) & result.asset_type.isin(classes)]
sort = st.selectbox("Sort by", ["name"] + INDICATORS)
ascending = st.checkbox("Ascending", value=True)
result = result.sort_values(sort, ascending=ascending, na_position="last")
st.caption(f"{len(result)} displayed / {len(assets)} imported; {assets.eligibility.eq('verified').sum()} verified eligible in the imported universe.")
st.dataframe(result, use_container_width=True, hide_index=True,
    column_config={column: st.column_config.NumberColumn(column, format="%.2f%%") for column in INDICATORS})
st.download_button("Export filtered results", result.to_csv(index=False), "screened_assets.csv", mime="text/csv")
st.caption("Returns use calendar months. Volatility and drawdown use the trailing 12 months; drawdown is negative. Blank metrics mean unavailable. See data_status and price_date. No missing prices are filled.")
st.warning("Metrics are in each asset's quote currency, with no GBP FX conversion. Yahoo uses adjusted prices; CSV adjustment basis is supplied by you. These may differ from competition performance. Crypto volatility uses 365 days; other assets use 252. No score or buy/sell recommendations.")
