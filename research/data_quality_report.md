# Institutional research — Stage 1 data quality

Audit date: 15 October 2026. Offline extraction of the five requested files. No rankings, scores, recommendations, FX conversion or horizon blending.

## Inventory and provenance

- **imf**: `imf/dataset_2026-10-15T18_00_45.260729696Z_DEFAULT_INTEGRATION_IMF.RES_WEO_9.0.0.csv` — 8,502,418 bytes; 8202 × 79 CSV; utf-8-sig; delimiter ','. SHA-256 `f06c2f17a48e8166b30ca75b33c5aa532c6b824e298c2af97966252c8639a351`.
- **oecd**: `oecd/OECD.ECO.MAD,DSD_EO_DF_EO,,filtered,2026-10-15 20-01-45.csv` — 620,798 bytes; 2885 × 32 CSV; utf-8; delimiter ','. SHA-256 `2c6a8f7a28ae566aba6fe971c0afe1d6d51234fcae19940deccf035506270c11`.
- **schwab**: `schwab/schwab_sector_outlook_2026-10-02.pdf` — 1,330,672 bytes; 11 PDF pages. SHA-256 `74733eaed6c919576a456d01296c0ce0b70eed32db11fcdb0dd8a6319c42f593`.
- **vanguard**: `vanguard/vanguard_return_forecasts_2026-06-30.pdf` — 235,432 bytes; 6 PDF pages. SHA-256 `2997f790bb6ca9077e42847884e54ca666ae8dab21799492392a48d1e8cd0d92`.
- **jpmorgan**: `jpmorgan/matrix-usd.xlsx` — 229,237 bytes; sheet ['2026']; 59 labelled rows; worksheet extent 580 × 157. SHA-256 `e313d9142039f3836bceac91999f0e1c4346fe9ef1fd36b639a06e0c069ff57a`.

Every output joins by `source_id` to `processed/inventory.json` for the exact filename, SHA-256, publisher URL and metadata evidence. IMF observations additionally join by `SERIES_CODE` to `imf_series.csv` for indicators, units, scaling, currency and source publication date. Source row numbers count logical CSV records (header = 1); IMF quoted multiline metadata means they are not physical line numbers. PDF page numbers and Excel cell addresses are retained.

## Successfully extracted observations

| Dataset | Output rows | Finite numeric / usable categories | Missing or invalid |
|---|---:|---:|---:|
| imf_observations | 426,504 | 361,508 | 64,996 |
| oecd_observations | 2,885 | 2,885 | 0 |
| schwab_sector_outlook | 11 | 11 | 0 |
| vanguard_return_ranges | 3 | 3 | 0 |
| jpmorgan_assumptions | 177 | 177 | 0 |

imf_observations usable classification counts: `{"estimate_or_projection": 7750, "forecast": 38694, "historical_actual": 233797, "historical_status_unknown": 81267}`.

oecd_observations usable classification counts: `{"current_year_estimate_or_forecast": 58, "forecast": 58, "historical_status_unknown": 2769}`.

The numeric count includes historical observations; it is not a forecast count. Schwab rows are qualitative opinions, not numerical forecasts. Vanguard rows each contain a lower/upper range, not two independent forecasts. J.P. Morgan has three metrics per labelled assumption, including inflation (not an investable asset).

## IMF

8,202 annual series; 145 indicator codes/labels; 210 country/group identifiers. Annual columns 1980–2031. Publication/update is 13 October 2026 (`2026-10-13T02:00:00Z`), not the filename's download time. Countries include US, UK, euro-area economies, Japan, China, India and emerging economies; groups include World, G7, EU, Euro Area, advanced/emerging markets and regional aggregates. Commodity series are also present. Identifiers come from `COUNTRY.INDICATOR.A`; aggregate codes are not assumed ISO countries.

Indicators cover nominal/real/PPP GDP and growth/per capita, CPI levels and average/end-period inflation, GDP deflator, unemployment/employment/population, investment/savings, fiscal revenue/expenditure/balances/debt, current/financial accounts, trade volumes, external debt/service, output gaps, and commodity prices/indices. Full indicator labels/codes and geography lists are in the metadata tables/inventory; not every indicator is available for every geography.

Units are source percent, index, domestic currency, USD, PPP international dollars and commodity-specific prices; scales are units, millions or billions. Values are preserved at source scale. No currency is assigned to unitless growth rates; domestic/PPP/USD metrics keep distinct currency descriptions. Empty source UNIT fields remain empty; metric text still describes per-capita/PPP meanings. Fiscal/calendar-year, base-year and methodology fields are retained.

`LATEST_ACTUAL_ANNUAL_DATA` is used only when it is a plain year. Post-cutoff values at/before publication year are estimates/projections, not confirmed future forecasts; 2027–2031 values are future-period projections by temporal inference. FY strings, blanks and 'Not applicable' are not silently converted to a calendar-year cutoff. Missing annual cells are kept with a missing status and never replaced with zero. Future-year coverage is incomplete and is counted only where a numeric value exists.

## OECD

The supplied filtered EO119 CSV has just **GDPV_ANNPCT: real GDP volume growth**, annual, percent per annum (`PA`, multiplier 0), 1961–2027, across 58 country/group identifiers. It does not contain the OECD's full inflation, employment or other forecast dataset. It includes US/UK/Japan/China/India, OECD countries and selected non-members, plus OECD, World, non-OECD, EA17 and other aggregates. EA17 is not interchangeable with IMF Euro Area membership.

Publication date is externally confirmed as 3 June 2026 for Economic Outlook 119 / 2026/1; the CSV contains no release date, data cutoff or populated OBS_STATUS. All currencies are blank, appropriate for a volume growth rate. 2027 is future-period forecast by date; 2026 is labelled current-year estimate-or-forecast using the release context, not an official observation status. Earlier rows retain unknown actual/estimate status. Base-year and all original dimensions are retained. Obtain EO119 last-historical-point metadata before claiming exact actual/forecast cutoffs per country.

## Schwab

Publication and ratings as-of date: **2026-10-02**, rather than the PDF print date. PDF extraction status: **checked_against_local_pdf**. US S&P 500/GICS sectors only; six- to twelve-month relative outlook. Extracted ratings are cross-checked between the printed table and the commentary. Only `checked_against_local_pdf` means the current file hash and values also match the recorded visual review; `unverified_pdf` requires a fresh review. Supporting positive/risk prose is retained as extracted evidence, with page locators, and is not an independently validated forecast. Currency is not applicable to qualitative ratings.

| Sector | Qualitative rating |
|---|---|
| Communication Services | Less Favored |
| Consumer Discretionary | Least Favored |
| Consumer Staples | Neutral |
| Energy | More Favored |
| Financials | More Favored |
| Health Care | More Favored |
| Industrials | More Favored |
| Information Technology | Neutral |
| Materials | More Favored |
| Real Estate | Least Favored |
| Utilities | Less Favored |

Evidence covers AI/electrification investment and cyclical risks in industrials/materials, yield-curve support and credit risk in financials, innovation/regulatory risks in health care, and financing/valuation/consumer-demand pressures elsewhere. The local processed table preserves each sector's positive and negative rationale. Trailing six/twelve-month performance and concentration figures elsewhere in the PDF are historical context and are not extracted as forecasts. Categories remain text; no numeric favourability scores are assigned.

## Vanguard

Actual publication: **2026-07-22** (22 July 2026 in the audited snapshot); model run/as-of: **2026-06-30**. The filename gives the model date. PDF extraction status: **checked_against_local_pdf**. The table contains only exact 10-year annualised **nominal total-return ranges, USD**, from the p. 2 narrative. The three ranges in the audited snapshot were visually checked; changed files/values require a fresh review. They are central bands around the model's median, not confidence intervals or a full outcome distribution. No midpoint is manufactured.

| Asset class | Lower (%) | Upper (%) | Horizon |
|---|---:|---:|---|
| U.S. equities | 4.2 | 6.2 | 10 years |
| Developed markets ex-U.S. equities (unhedged) | 4.5 | 6.5 | 10 years |
| Emerging markets equities (unhedged) | 2 | 4 | 10 years |

The p. 3 chart contains additional equity, bond, commodity, inflation and currency labels and graphical ranges. Automatic table extraction yields labels and repeated axis text, **not numeric endpoint cells**. Visual inspection confirms a chart rather than a usable numeric table; the p. 2 horizon selector also visually highlights 30 years while the following chart says 10-year. Only explicitly 10-year narrative numbers are used. Fixed-income numbers, chart-only equities, median volatility, tail percentiles and all 30-year numeric forecasts remain unavailable. No pixel/axis estimates, OCR guesses or 10-to-30-year extrapolations are produced.

PDF review status is bound to SHA-256 and exact extracted ratings/ranges in `pdf_review.json`. A different file or different values returns `unverified_pdf`; it cannot inherit the review. Partial/missing narrative ranges produce issues instead of placeholder observations. Model outcomes remain hypothetical even when extraction is checked.

## J.P. Morgan

Actual workbook sheet: **2026**. A2 explicitly says **2026 Long-Term Capital Market Assumptions – USD**. Rows 9–67 hold 59 labelled assumptions, including inflation. Column C = 2026 compound return; D = 2026 arithmetic return; E = annualised volatility. Column F is prior-vintage 2025 compound return and is intentionally excluded; G:BM is the lower-triangular correlation matrix, also excluded. Merged header cells B5–B8 label these columns in reverse vertical order; blindly treating the first nonempty row as flat headers would be wrong. The 580 × 157 worksheet extent includes formatting and is not 580 observations.

177 finite numeric cells are extracted at original percentage-point scale; 6.7 means 6.7%, not 670%. Sample cross-check: U.S. Large Cap C31 = 6.7, D31 = 7.935086973158945, E31 = 16.47014248435096; UK Large Cap C37 = 6.6000000000000005. Workbook numbers are compared directly in tests. Printed matrix pp. 82–83 confirms column ordering and rounded values.

The **2026** label is an assumptions vintage, not a calendar-2026 return forecast. The official release dated **20 October 2025** specifies a **10–15-year** horizon; official matrix notes give **30 September 2025** as-of and nominal USD assumptions. These dates/horizon are external metadata, explicitly distinguished from workbook extraction. The workbook's 15 October 2025 modified timestamp is not its release date. A companion `ltcma-full-report.pdf` was also found locally during inspection and used only as a matrix cross-check; it is not a sixth ingestion input or required at runtime.

Coverage includes US, euro area, Japan, Hong Kong, UK, China, EAFE, emerging markets, Asia ex-Japan and global asset classes, plus real assets/private markets. Printed source groups are retained without inventing sector classifications. FX hedge/local-currency wording remains part of the exact asset label; USD investor-return currency does not mean every underlying security is USD-denominated. Alternatives are median-manager estimates net of fees; equity/bond assumptions are not active-manager alpha forecasts. A1 restricts this workbook to institutional/wholesale/professional/qualified investors and says not for retail use or distribution.

## Compatibility and sufficiency for a sector × region ranking

**Not sufficient for a defensible sector × region ranking.** Macro country GDP/inflation is not sector earnings or equity return. Schwab covers only US sectors, qualitatively over 6–12 months. Vanguard covers broad asset classes over 10 years with only three exact ranges recoverable here. J.P. Morgan covers broad asset classes over 10–15 years from a different vintage. None supplies a consistent non-US GICS sector panel. These data are therefore emitted separately, with no ranking, aggregation, sector imputation or horizon conversion.

Other incompatibilities: nominal vs real/PPP macro variables; rate vs level and millions/billions; domestic vs USD/PPP currency; FX hedge basis; arithmetic vs compound/geometric returns; net alternative-manager fees vs index assumptions; different release/as-of dates and fiscal calendars; nonmatching regional membership and aggregation weights; qualitative categories vs numerical ranges/point assumptions. No crosswalk equates similarly named aggregates.

A later heatmap needs a defined investment horizon and common as-of vintage, licensed sector-by-region earnings/revenue revisions, valuations, profitability and balance-sheet data, consistent GICS taxonomy and country/region membership, investable benchmark/asset identifiers and competition eligibility. It also needs comparable price/total-return/volatility data, FX/base-currency and hedging policy, and consistent sector weights, coverage and missingness. For outlook comparisons obtain non-US sector views at the same horizon, machine-readable Vanguard tables with volatility/percentiles, and OECD latest-actual metadata. Historical validation and explicit uncertainty/coverage rules would be needed before choosing any ranking method; no scoring is attempted in Stage 1.

## Extraction limitations and licensing

The pipeline is offline and schema-specific. It rejects changed CSV layouts, unknown sectors/ratings, inconsistent table/commentary, wrong workbook vintage/currency and missing inputs. Numeric tokens retain raw values and missing/invalid status. It neither executes Excel formulas nor reconstructs missing cached values. It does not infer chart numbers. Source URLs describe publisher provenance; original browser transfer URLs were not recorded. PDF print metadata can expose local download times and is not used as publication evidence. Re-running with changed content requires renewed PDF review and report assessment.

Downloaded files and **all derived data** in `research/processed/` are gitignored pending redistribution review. Code, metadata, tests and this limited audit report can be reviewed without publishing the source archive. Existing blank `research/sources.csv` is not treated as evidence. Supporting links were checked 15 October 2026; no broad republication rights are inferred from public download availability.

- [IMF statistical-data terms](https://www.imf.org/en/about/copyright-and-terms) allow attributed data reuse subject to their conditions; different terms apply to other content/third-party data and potential commercial use. Preserve IMF attribution and original metric meanings.
- [OECD terms, Data section](https://www.oecd.org/en/about/terms-conditions.html) permit attributed data reuse subject to dataset/third-party restrictions. Preserve the EO119 citation and verify any source-specific rights before redistribution.
- Schwab and Vanguard PDFs contain all-rights-reserved notices. Their availability is not a redistribution licence. Keep raw PDFs and extracted prose/tables local pending appropriate permission.
- J.P. Morgan's workbook audience/use restriction is explicit. Do not publish the workbook or derived matrix as a retail product; confirm permitted use and redistribution with the publisher before deployment.

## Date/horizon verification sources

- [IMF WEO source](https://data.imf.org/en/datasets/IMF.RES:WEO): exact release timestamp comes from the supplied CSV.
- [OECD Economic Outlook](https://www.oecd.org/en/topics/sub-issues/economic-outlook.html) and [EO119 explorer](https://data-explorer.oecd.org/?df[ag]=OECD.ECO.MAD&df[id]=DSD_EO@DF_EO&df[vs]=1.5): 3 June 2026 release, edition 2026/1.
- [Schwab sector outlook](https://www.schwab.com/learn/story/stock-sector-outlook): local PDF dated 2 October 2026.
- [Vanguard VCMM](https://corporate.vanguard.com/content/corporatesite/us/en/corp/vemo/vemo-return-forecasts.html): local PDF separates publication and model-run date.
- [J.P. Morgan 2026 release](https://am.jpmorgan.com/us/en/asset-management/adv/about-us/media/press-releases/jp-morgan-releases-2026-long-term-capital-market-assumptions/) and [official matrix report](https://am.jpmorgan.com/content/dam/jpm-am-aem/global/en/insights/portfolio-insights/ltcma/noindex/ltcma-full-report.pdf), pp. 82–83: release, horizon, as-of, currency and return conventions.
