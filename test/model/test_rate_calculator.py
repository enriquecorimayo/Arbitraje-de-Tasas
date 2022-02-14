import src.model.rate_calculator as rc
import src.model.market_apis as mapis
from src.model.instrument_handler import FutureContract

import unittest
from unittest.mock import MagicMock, Mock, patch
import datetime as dt
from freezegun import freeze_time


class TestRateCalculator(unittest.TestCase):
    NOW_DATE = "2022-01-01"

    def setUp(self):
        self._spot_price = 100
        self._yfinance_api_mock = MagicMock()
        self._yfinance_api_mock.last_prices.return_value = {
            "GGAL": self._spot_price,
            "PAMP": self._spot_price,
        }

        self._pyrofex_api_mock = MagicMock()
        self._pyrofex_api_mock.bids.return_value = {
            "GGAL/FEB22": mapis.OrderBook(110, 10),
            "PAMP/FEB22": mapis.OrderBook(120, 10),
        }
        self._pyrofex_api_mock.asks.return_value = {
            "GGAL/FEB22": mapis.OrderBook(115, 10),
            "PAMP/FEB22": mapis.OrderBook(130, 10),
        }
        self._tradeable_check_mock = MagicMock()
        self._maturity_date = dt.datetime(2022, 5, 28, 0, 0, 0, 0)
        self._tradeable_check_mock.tradeable_pyrofex_future_underlier_ticker.return_value = {
            "GGAL": [FutureContract("GGAL/FEB22", "GGAL", self._maturity_date, 100.0)],
            "PAMP": [FutureContract("PAMP/FEB22", "PAMP", self._maturity_date, 100.0)],
        }
        self._tradeable_check_mock.tradeable_ticker_maturity.return_value = {
            "GGAL/FEB22": "FEB22",
            "PAMP/FEB22": "FEB22",
        }
        self._implicit_rate_calculator = rc.ImplicitRateCalculator(
            self._pyrofex_api_mock, self._yfinance_api_mock, self._tradeable_check_mock
        )

    @freeze_time(NOW_DATE)
    def test_update_rates_using_implicit_rate_to_set_prices(self):
        static_max_buy_rate = 0.55
        static_min_sell_rate = 0.50
        days_to_expire = (self._maturity_date - dt.datetime.now()).days
        max_taker_price = (
            1 + static_max_buy_rate / self._implicit_rate_calculator.DAYS_IN_A_YEAR
        ) ** days_to_expire * self._spot_price
        min_offered_price = (
            1 + static_min_sell_rate / self._implicit_rate_calculator.DAYS_IN_A_YEAR
        ) ** days_to_expire * self._spot_price

        self._pyrofex_api_mock.bids.return_value = {
            "GGAL/FEB22": mapis.OrderBook(100, 10),
            "PAMP/FEB22": mapis.OrderBook(max_taker_price, 10),
        }
        self._pyrofex_api_mock.asks.return_value = {
            "GGAL/FEB22": mapis.OrderBook(min_offered_price, 10),
            "PAMP/FEB22": mapis.OrderBook(500, 10),
        }
        self._implicit_rate_calculator.update_rates()
        _, max_buy_rate = self._implicit_rate_calculator.max_buy_rate("FEB22")
        _, min_sell_rate = self._implicit_rate_calculator.min_sell_rate("FEB22")
        self.assertAlmostEqual(static_max_buy_rate, max_buy_rate, 10)
        self.assertAlmostEqual(static_min_sell_rate, min_sell_rate, 10)

    @freeze_time(NOW_DATE)
    def test_update_rates_when_arb_exist(self):
        self._implicit_rate_calculator.update_rates()
        _, max_buy_rate = self._implicit_rate_calculator.max_buy_rate("FEB22")
        _, min_sell_rate = self._implicit_rate_calculator.min_sell_rate("FEB22")
        self.assertTrue(max_buy_rate > min_sell_rate)

    @freeze_time(NOW_DATE)
    def test_update_rates_when_there_is_no_arb_opportunity(self):
        self._pyrofex_api_mock.bids.return_value = {
            "GGAL/FEB22": mapis.OrderBook(110, 10),
            "PAMP/FEB22": mapis.OrderBook(115, 10),
        }
        self._pyrofex_api_mock.asks.return_value = {
            "GGAL/FEB22": mapis.OrderBook(120, 10),
            "PAMP/FEB22": mapis.OrderBook(125, 10),
        }
        self._implicit_rate_calculator.update_rates()
        _, max_buy_rate = self._implicit_rate_calculator.max_buy_rate("FEB22")
        _, min_sell_rate = self._implicit_rate_calculator.min_sell_rate("FEB22")
        self.assertTrue(max_buy_rate < min_sell_rate)


if __name__ == "__main__":
    unittest.main()
