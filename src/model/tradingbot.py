from src.model.instrument_handler import InstrumentHandler
from src.model.tradeable_check import TradeableCheck
from src.model.market_apis import PyRofexApi
from src.model.market_apis import YfinanceAPI
from src.model.update_data import DataUpdate
from src.model.rate_calculator import ImplicitRateCalculator
from src.model.display import Display
from src.model.strategy import Strategy

import traceback
import time


class TradingBot:
    def __init__(self, tickers, underlier_update_frecuency):
        self._instrument_handler = InstrumentHandler(tickers)
        self._tradeable_check = TradeableCheck(tickers)
        self._pyrofex_api = PyRofexApi(self._tradeable_check)
        self._yfinance_api = YfinanceAPI(
            self._instrument_handler, underlier_update_frecuency, self._tradeable_check
        )
        self._data_update = DataUpdate(self._pyrofex_api, self._yfinance_api)
        self._implicit_rate_calculator = ImplicitRateCalculator(
            self._pyrofex_api, self._yfinance_api, self._tradeable_check
        )
        self._display = Display(self._implicit_rate_calculator)
        self._strategy = Strategy(
            self._instrument_handler,
            self._implicit_rate_calculator,
            self._pyrofex_api,
            self._yfinance_api,
            self._data_update,
            self._tradeable_check,
        )

    def start(self):
        self._run()
        self._end()

    def _run(self):
        self._yfinance_api.request_market_data()
        self._pyrofex_api.request_market_data()
        while True:
            try:
                if self._data_update.update_boolean():
                    self._data_update.give_last_update()
                    self._implicit_rate_calculator.update_rates()
                    if self._implicit_rate_calculator.ready():
                        try:
                            self._display.print_implicit_rates()
                        except Exception:
                            print(
                                f"Excepción mientras se muestran las tasas implícitas..."
                            )
                        self._strategy.start_trades()
            except Exception as e:
                traceback.print_exc()
                print(f"Excepción mientras se tradeaba...")
                break
            if not self._yfinance_api.start_request():
                self._yfinance_api.request_market_data()
            if not self._pyrofex_api.start_request():
                self._pyrofex_api.request_market_data()

    def _end(self):
        print("Cerrando...")
        self._yfinance_api.stop()
        self._pyrofex_api.stop()
        print("Listo!")
