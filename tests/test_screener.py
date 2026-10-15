import io
import math
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd
from data import load_assets, load_prices, fetch_prices
from screener import screen_assets, INDICATORS


class ScreenerTests(unittest.TestCase):
    def setUp(self):
        self.assets = pd.DataFrame([dict(asset_id="a", name="Example", asset_type="stock")])
        self.dates = pd.bdate_range("2024-12-20", "2026-01-02")
        self.prices = pd.DataFrame(dict(asset_id="a", date=self.dates,
                                       close=100.0, currency="USD"))

    def screen(self, prices=None, as_of="2026-01-02"):
        return screen_assets(self.assets, self.prices if prices is None else prices, as_of).iloc[0]

    def test_known_returns_and_drawdown(self):
        self.prices.loc[self.prices.date >= "2025-07-02", "close"] = 200
        self.prices.loc[self.prices.date == "2026-01-02", "close"] = 150
        result = self.screen()
        self.assertAlmostEqual(result.return_6m_pct, -25)
        self.assertAlmostEqual(result.return_12m_pct, 50)
        self.assertAlmostEqual(result.max_drawdown_pct, -25)
        window = self.prices.set_index("date").close.loc["2025-01-02":]
        self.assertAlmostEqual(result.volatility_pct, window.pct_change().dropna().std(ddof=1) * math.sqrt(252) * 100)

    def test_constant_prices_are_real_zeroes(self):
        self.assertTrue(self.screen()[INDICATORS].eq(0).all())

    def test_short_sparse_stale_or_empty_history_is_unavailable(self):
        for prices in (self.prices.tail(50), self.prices.iloc[::10], pd.DataFrame()):
            self.assertTrue(self.screen(prices)[INDICATORS].isna().all())
        self.assertTrue(self.screen(as_of="2026-02-01")[INDICATORS].isna().all())

    def test_six_month_only(self):
        result = self.screen(self.prices[self.prices.date >= "2025-06-01"])
        self.assertEqual(result.return_6m_pct, 0)
        self.assertTrue(pd.isna(result.return_12m_pct))
        self.assertTrue(pd.isna(result.volatility_pct))

    def test_invalid_prices_not_filled(self):
        self.prices.loc[20:80, "close"] = float("nan")
        self.assertTrue(self.screen()[["return_12m_pct", "volatility_pct", "max_drawdown_pct"]].isna().all())

    def test_duplicate_and_mixed_currency_block_metrics(self):
        duplicate = pd.concat([self.prices, self.prices.tail(1)])
        self.assertTrue(self.screen(duplicate)[INDICATORS].isna().all())
        self.prices.loc[0, "currency"] = "GBP"
        self.assertTrue(self.screen()[INDICATORS].isna().all())

    def test_crypto_uses_365_days(self):
        self.assets["asset_type"] = "crypto"
        dates = pd.date_range("2025-01-01", "2026-01-02")
        prices = pd.DataFrame(dict(asset_id="a", date=dates, currency="USD",
                                  close=[100 + i % 7 for i in range(len(dates))]))
        window = prices.set_index("date").close.loc["2025-01-02":]
        self.assertAlmostEqual(self.screen(prices).volatility_pct,
                               window.pct_change().dropna().std() * math.sqrt(365) * 100)

    def test_legacy_csv_and_evidence(self):
        prices = load_prices(io.StringIO("asset_id,date,close_gbp\n001,2026-01-01,5\n"))
        self.assertEqual(prices.asset_id.iloc[0], "001")
        self.assertEqual(prices.currency.iloc[0], "GBP")
        header = "asset_id,name,asset_type,ticker,isin,eligibility,verified_at,source\n"
        with self.assertRaises(ValueError):
            load_assets(io.StringIO(header + "001,Example,stock,,,verified,,\n"))
        self.assertEqual(load_assets(io.StringIO(header + "001,Example,stock,,,,,\n")).eligibility.iloc[0], "unverified")

    def test_provider_mapping_and_failure(self):
        assets = self.assets.assign(yahoo_ticker="EXAMPLE")
        ticker = MagicMock()
        ticker.history.return_value = pd.DataFrame({"Close": [100, 101]},
            index=pd.date_range("2026-01-01", periods=2, tz="UTC"))
        ticker.get_history_metadata.return_value = {"currency": "USD"}
        with patch("yfinance.Ticker", return_value=ticker) as factory:
            prices, errors = fetch_prices(assets)
            factory.assert_called_once_with("EXAMPLE")
            self.assertEqual(len(prices), 2)
            self.assertEqual(errors, [])
            ticker.history.side_effect = RuntimeError("unavailable")
            prices, errors = fetch_prices(assets)
            self.assertTrue(prices.empty)
            self.assertIn("unavailable", errors[0])
        prices, errors = fetch_prices(self.assets)
        self.assertTrue(prices.empty)
        self.assertIn("no yahoo_ticker", errors[0])

    def test_dashboard_starts(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
        self.assertEqual(len(app.exception), 0)
        self.assertIn("V0.2", app.title[0].value)

    def test_dashboard_import_filter_sort_export(self):
        from streamlit.testing.v1 import AppTest
        asset_csv = "asset_id,name,asset_type,ticker,isin,eligibility,verified_at,source\n" + "a,Example,stock,EX,,unverified,,\n"
        prices = self.prices.copy()
        prices["date"] += pd.Timestamp.today().normalize() - prices.date.max()
        app_path = str(Path(__file__).resolve().parents[1] / "app.py")
        def upload(label, **kwargs):
            return io.StringIO(asset_csv if "universe" in label else prices.to_csv(index=False))
        with patch("streamlit.file_uploader", side_effect=upload):
            app = AppTest.from_file(app_path).run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(len(app.dataframe[0].value), 1)
            app.selectbox[0].set_value("return_6m_pct").run()
            self.assertEqual(app.dataframe[0].value.return_6m_pct.iloc[0], 0)
            self.assertEqual(len(app.get("download_button")), 3)
            app.multiselect[0].set_value(["verified"]).run()
            self.assertTrue(app.dataframe[0].value.empty)
            self.assertEqual(len(app.exception), 0)


if __name__ == "__main__":
    unittest.main()
