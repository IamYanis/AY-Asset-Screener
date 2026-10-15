import pandas as pd
import streamlit as st
from screener import load_assets, rank_assets, TYPES

st.set_page_config(page_title="A-Y Asset Screener", layout="wide")
st.title("A-Y Asset Screener — V0.1")
st.caption("Multi-asset competition research. Eligibility must be verified in UMushroom.")

asset_file = st.file_uploader("Import asset universe CSV", type="csv")
price_file = st.file_uploader("Import GBP price histories CSV (optional)", type="csv")
st.download_button("Download blank asset CSV", "asset_id,name,asset_type,ticker,isin,eligibility,verified_at,source\n", "assets_template.csv")
st.download_button("Download blank price CSV", "asset_id,date,close_gbp\n", "prices_template.csv")

if asset_file is None:
    st.info("Import an asset universe CSV to start. Only assets explicitly marked 'verified' will be described as eligible.")
    st.stop()

try:
    assets = load_assets(asset_file)
    prices = pd.read_csv(price_file) if price_file is not None else pd.DataFrame()
    result = rank_assets(assets, prices)
except (ValueError, pd.errors.ParserError) as exc:
    st.error(str(exc))
    st.stop()

status = st.multiselect("Eligibility", ["verified", "unverified", "ineligible"], default=["verified", "unverified"])
classes = st.multiselect("Asset class", sorted(TYPES), default=sorted(TYPES))
result = result[result.eligibility.isin(status) & result.asset_type.isin(classes)]
col1, col2, col3 = st.columns(3)
col1.metric("Imported assets", len(assets))
col2.metric("Verified eligible", (assets.eligibility == "verified").sum())
col3.metric("Unverified", (assets.eligibility == "unverified").sum())
st.dataframe(result, use_container_width=True, hide_index=True)
st.download_button("Export filtered results", result.to_csv(index=False), "screened_assets.csv", mime="text/csv")
st.caption("The 30-observation return is an illustrative price-history sort, not a comparable asset-quality score. Missing history remains blank. All prices must be supplied in GBP; no automatic FX conversion is performed.")
