from src.model.instrument_handler import InstrumentHandler
from src.model.tradeable_check import TradeableCheck
from src.model.market_apis import PyRofexApi
from src.model.market_apis import YfinanceAPI

import traceback
import time


class TradingBot:
    """
    Clase que instancia a las demas clases y se encarga de correr el Bot

    """
    
    def __init__(self, tickers):
        self._instrument_handler = InstrumentHandler(tickers)
        self._tradeable_check = TradeableCheck(tickers)
        self._yfinance_api = YfinanceAPI(
            self._instrument_handler, self._tradeable_check
        )
        self._pyrofex_api = PyRofexApi(
            self._instrument_handler, self._tradeable_check, self._yfinance_api
        )

    def start(self):
        self._yfinance_api.request_market_data()
        self._pyrofex_api.request_market_data()
