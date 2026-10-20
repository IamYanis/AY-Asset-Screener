# Institutional ingestion — Stage 1

This offline pipeline inspects the five supplied snapshots and produces separate structured datasets. It does not change the Streamlit screener, combine forecast horizons, generate scores or give investment recommendations.

```bash
# From the repository root, using the existing virtual environment:
pip install -r requirements.txt -r research/requirements.txt
python -m research.ingest
python -m unittest discover -s tests -v
```

`pdfplumber` and `openpyxl` are optional research dependencies; the dashboard needs no changes or additional dependencies. No scraping, API calls, database or Excel formula execution is involved.

Put the five files under `research/institutional/` using the paths in `source_metadata.json`. CSV discovery requires exactly one file per IMF/OECD folder; ambiguous inputs fail explicitly. PDFs and workbook use the exact named snapshots. An optional J.P. Morgan full-report PDF found locally was consulted to check the matrix layout but is not an ingestion input. All five required inputs must exist; extraction errors fail the command rather than creating placeholder observations. No files in the input directory are modified.

Outputs are written to `research/processed/` and the audit to [data_quality_report.md](data_quality_report.md). Other output locations are supported with `--output-dir /path/to/processed` (the report goes alongside that directory); `--input-dir` selects another copy of the source tree. All inputs are parsed before outputs are written. Outputs replace the same filenames on reruns and use deterministic row ordering. No current timestamp is added to the data; the report/review refer to the audited 15 October 2026 snapshots.

| Output | Meaning |
|---|---|
| `inventory.json` | Five source IDs, exact filenames, SHA-256 hashes, sizes, detected formats/headers/dimensions, dates, publisher links and date evidence |
| `summary.json` | Generated row, numeric/missing/invalid and temporal classification counts |
| `imf_series.csv` | All source metadata per `SERIES_CODE`, country/metric codes and cautiously derived currency description; units/scales/methodology are retained |
| `imf_observations.csv` | Long annual cells, including blanks: raw/numeric value, status, year, source row/column, temporal classification and years relative to release |
| `oecd_observations.csv` | Original dimensions plus value/status, source row, externally sourced release date and conservative temporal classification |
| `schwab_sector_outlook.csv` | Eleven US sector ratings as text, six–twelve month horizon, benchmark, positive/risk evidence and page locators |
| `vanguard_return_ranges.csv` | Three exact 10-year narrative return ranges in nominal USD, dates, page/evidence, range definition and extraction status |
| `jpmorgan_assumptions.csv` | 59 labelled assumptions × three metrics, original numeric scale, exact Excel cells, USD, vintage and externally confirmed 10–15 year horizon |

Every table has `source_id`, which joins to the inventory for filenames, hashes and provenance. Join IMF observations to `imf_series.csv` on `SERIES_CODE` for units, scale and publication date; this avoids repeating several megabytes of metadata for every annual cell. `source_row` counts logical CSV records, not physical lines, because IMF notes include embedded newlines. Excel has exact worksheet/cell locators. Source units are not normalised into a common economic measure: billions, indices, percent, USD and domestic currencies keep their meanings. `raw_value` is retained; numeric blank/invalid values stay empty with an explicit status. Zero and negative values are valid.

IMF plain-year latest-actual cutoffs are respected. FY-labelled/absent cutoffs remain ambiguous. Future years are labelled forecast by date, not by invented source observation flags. OECD's OBS_STATUS is empty; 2026 is current-year estimate-or-forecast, 2027 is future-period forecast, and earlier actual/estimate status is unknown. These are operational classifications with `classification_basis`, not claims about official per-cell status.

PDF text/tables are not automatically trusted. The audit checked rendered local pages against extracted dates, all Schwab table ratings and Vanguard's three narrative ranges. `pdf_review.json` binds that review to exact file hashes and values. Changes produce `unverified_pdf`; no review is inherited solely because a filename matches. The review records checked transcription, not the reliability of any forecast. Supporting Schwab prose remains labelled extracted/unvalidated evidence. Vanguard's chart contains graphical ranges without numeric table cells: chart-only numbers, volatility and 30-year projections are deliberately not extracted. There is no OCR or graph digitisation.

`source_metadata.json` contains externally checked publication/horizon evidence where absent from the file. The J.P. Morgan sheet title confirms USD and 2026 vintage; the official release/report confirms October 2025 publication, September 2025 as-of and 10–15 years. The year in a file/sheet name is not assumed to be the publication date or a one-year forecast horizon. Publisher landing-page links are provenance context, not a claim that an original browser transfer URL was recorded.

The tests use synthetic CSV/Excel/PDF files in temporary directories and check malformed layouts, missingness, currency, horizons and review invalidation. Additional integration tests use the actual local sources, compare all IMF raw year cells, all OECD numeric values and all 177 extracted Excel cells, and assert manually checked PDF values. Source-local tests skip when the downloaded files are absent; test output makes that explicit. No synthetic test values are used in the pipeline's production outputs.

Raw sources and all generated processed tables are gitignored pending redistribution review. The report records rights considerations, especially the workbook's explicit professional/institutional audience restriction. Local extraction does not confer publication rights. See the report for why these datasets are **insufficient for a defensible sector × region ranking** and which compatible sector data would be needed next.
