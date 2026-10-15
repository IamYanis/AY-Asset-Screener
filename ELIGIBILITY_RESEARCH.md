# UK 2026 eligibility investigation

Checked 15 October 2026. No complete, public UK 2026 competition-eligible catalogue, documented API, or explicitly permitted bulk export was found in the official pages and targeted searches below. This is a limited public-source finding, not proof that an organiser-provided export does not exist. No assets or classes have been independently confirmed eligible for UK 2026 in this repository.

- [UK 2026 competition page](https://umushroom.com/en/contest/uk-investment-competition-2026) and [conditions page](https://umushroom.com/en/contest/uk-investment-competition-2026/conditions-of-participation): the publicly rendered text mentions CHF, Swiss residence and March–April 2025. It mentions stocks, crypto, ETFs and funds, but the stale content cannot establish UK 2026 rules.
- [Official FAQ/contact](https://umushroom.com/en/contact): describes a global investment universe and a green flag restriction for funds/ETFs. It also contains historical Swiss contest references and inconsistent crypto availability text. Platform availability and these general FAQs do not establish UK competition eligibility.
- [Terms of use](https://umushroom.com/en/terms-of-use), section 4(c): restrict systematic automated extraction. No scraping or private endpoint discovery is implemented.

Searches covered the official domain for UK 2026 eligibility, API, catalogue and export documentation. Public investment browsing is not a competition-specific eligible export. We have not accessed a participant account, requested permission, or contacted organisers.

## Practical fallback

Ask organisers through the official contact page for the current UK 2026 rulebook and a permitted eligible-asset CSV/API, including asset class, ISIN or other stable ID, exchange/share class, and restrictions. Until provided, use your own permitted CSV. Confirm each exact instrument in the UK 2026 competition's Add Investments interface or an organiser-supplied list, record its source and verification date, then mark it `verified`. Record rejected instruments as `ineligible`; leave all others `unverified`. Recheck before selection; evidence fields are user assertions, not independently validated by the app.

The importer retains V0.1's stock, ETF, fund, crypto, bond and other categories so it can accept later confirmations without code changes. Supporting a category is not confirmation that the competition permits it. No sample instrument is labelled eligible.
