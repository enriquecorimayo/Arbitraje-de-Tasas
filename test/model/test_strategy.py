import unittest
from unittest.mock import MagicMock, Mock, patch
from freezegun import freeze_time
import datetime as dt
import pyRofex
import src.model.strategy as stgy
from src.model.instrument_handler import FutureContract
import src.model.rate_calculator as rc
import src.model.market_apis as mapis


class TestStrategy(unittest.TestCase):

    NOW_DATE = "2022-01-01"

    def setUp(self):
        # Por simplicidad el spot price es el mismo para los dos instrumentos
        self._spot_price = 100.0
        self._yfinance_api_mock = MagicMock()
        last_prices = {"GGAL": self._spot_price, "PAMP": self._spot_price}
        self._yfinance_api_mock.last_prices.return_value = last_prices
        self._yfinance_api_mock.price.side_effect = lambda ticker: last_prices[ticker]

        self._pyrofex_api_mock = MagicMock()
        self._pyrofex_api_mock.bids.return_value = {
            "GGAL/FEB22": mapis.OrderBook(110, 10),
            "PAMP/FEB22": mapis.OrderBook(120, 10),
        }
        self._pyrofex_api_mock.asks.return_value = {
            "GGAL/FEB22": mapis.OrderBook(115, 10),
            "PAMP/FEB22": mapis.OrderBook(125, 10),
        }
        self._pyrofex_api_mock.place_order.return_value = {
            "order": {"clientId": "test_order_id"}
        }
        self._pyrofex_api_mock.order_execution_status.return_value = "UNITTEST"
        self._tradeable_check_mock = MagicMock()
        self._maturity_date = dt.datetime(2022, 5, 28, 0, 0, 0, 0)
        ggal_future = FutureContract("GGAL/FEB22", "GGAL", self._maturity_date, 100.0)
        PAMP_future = FutureContract("PAMP/FEB22", "PAMP", self._maturity_date, 100.0)
        self._tradeable_check_mock.tradeable_pyrofex_future_underlier_ticker.return_value = {
            "GGAL": [ggal_future],
            "PAMP": [PAMP_future],
        }
        self._instrument_handler_mock = MagicMock()
        self._instrument_handler_mock.rofex_instruments_by_ticker.return_value = {
            "GGAL/FEB22": ggal_future,
            "PAMP/FEB22": PAMP_future,
        }
        self._tradeable_check_mock.tradeable_ticker_maturity.return_value = {
            "GGAL/FEB22": "FEB22",
            "PAMP/FEB22": "FEB22",
        }
        self._tradeable_check_mock.tradeable_maturities.return_value = ["FEB22"]
        self._implicit_rate_calculator = rc.ImplicitRateCalculator(
            self._pyrofex_api_mock,
            self._yfinance_api_mock,
            self._tradeable_check_mock,
        )

        self._data_update_mock = MagicMock()
        self._data_update_mock.update_boolean.return_value = False

        self._strategy = stgy.Strategy(
            self._instrument_handler_mock,
            self._implicit_rate_calculator,
            self._pyrofex_api_mock,
            self._yfinance_api_mock,
            self._data_update_mock,
            self._tradeable_check_mock,
        )

    @freeze_time(NOW_DATE)
    def test_trader_when_there_is_no_arb_opportunity(self):
        self._pyrofex_api_mock.bids.return_value = {
            "GGAL/FEB22": mapis.OrderBook(110, 10),
            "PAMP/FEB22": mapis.OrderBook(115, 10),
        }
        self._pyrofex_api_mock.asks.return_value = {
            "GGAL/FEB22": mapis.OrderBook(120, 10),
            "PAMP/FEB22": mapis.OrderBook(125, 10),
        }
        self._implicit_rate_calculator.update_rates()
        self._strategy.start_trades()
        self.assertEqual(self._pyrofex_api_mock.place_order.call_count, 0)

    @freeze_time(NOW_DATE)
    def test_trader_when_arb_exist(self):
        self._implicit_rate_calculator.update_rates()
        self._strategy.start_trades()
        # Testea si se mandan 2 ordenes
        self.assertEqual(self._pyrofex_api_mock.place_order.call_count, 2)
        (
            buy_order_args,
            sell_order_args,
        ) = self._pyrofex_api_mock.place_order.call_args_list

        self.assertEqual(sell_order_args.kwargs["ticker"], "PAMP/FEB22")
        self.assertEqual(sell_order_args.kwargs["side"], pyRofex.Side.SELL)
        self.assertEqual(sell_order_args.kwargs["size"], 10)
        self.assertEqual(sell_order_args.kwargs["price"], 120)
        self.assertEqual(
            sell_order_args.kwargs["time_in_force"],
            pyRofex.TimeInForce.ImmediateOrCancel,
        )
        self.assertEqual(sell_order_args.kwargs["order_type"], pyRofex.OrderType.LIMIT)

        self.assertEqual(buy_order_args.kwargs["ticker"], "GGAL/FEB22")
        self.assertEqual(buy_order_args.kwargs["side"], pyRofex.Side.BUY)
        self.assertEqual(buy_order_args.kwargs["size"], 10)
        self.assertEqual(buy_order_args.kwargs["price"], 115)
        self.assertEqual(
            buy_order_args.kwargs["time_in_force"],
            pyRofex.TimeInForce.ImmediateOrCancel,
        )
        self.assertEqual(buy_order_args.kwargs["order_type"], pyRofex.OrderType.LIMIT)


if __name__ == "__main__":
    unittest.main()
