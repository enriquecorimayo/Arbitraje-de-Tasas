import re
import datetime as dt
from dateutil.parser import parse
from collections import defaultdict
import src.model.expired as exp
import src.model.api_wrapper as wrapper


class FutureContract:
    """
    Clase para representar un contrato de futuro
    """

    def __init__(self, ticker, underlier_ticker, maturity_date, future_contract_size):
        self._ticker = ticker
        self._underlier_ticker = underlier_ticker
        self._maturity_date = maturity_date
        self._future_contract_size = future_contract_size

    def __repr__(self):
        return f"{self._ticker} : [{self._underlier_ticker} - {self._maturity_date} - {self._future_contract_size}]"

    @property
    def ticker(self):
        return self._ticker

    @property
    def underlier_ticker(self):
        return self._underlier_ticker

    @property
    def maturity_date(self):
        return self._maturity_date

    @property
    def future_contract_size(self):
        return self._future_contract_size

    def time_to_expire(self, start_date=None):
        """
        Cuenta los días hasta el vencimiento del contrato.
        """
        start_date = start_date or dt.datetime.now()
        delta = self._maturity_date.date() - start_date.date()
        if delta.days + 1 <= 0:
            raise exp.ExpiredInstrument(self)
        return delta.days


class InstrumentHandler:
    """
    Obtiene el nombre de los tickers y obitiene los transforma tal que el nuevo formato sea compatible con
    yfinance y pyRofex.
    """

    def __init__(self, tickers):
        self._tickers = tickers
        self._pyrofex_future_underlier = defaultdict(list)
        self._pyrofex_future_maturity = defaultdict(list)
        self._convert_to_yfinance_ticker = {
            ticker: self.convertion(ticker) for ticker in tickers
        }
        self._reorder_yfinance_tickers = {
            v: k for k, v in self._convert_to_yfinance_ticker.items()
        }
        self._rofex_instruments_by_ticker = {}
        self._parse_rofex()

    @staticmethod
    def convertion(ticker):
        if ticker == "DLR":
            return "ARS=X"
        return ticker + ".BA"

    def futures_ticker(self):
        return list(self._rofex_instruments_by_ticker.keys())

    def yfinance_tickers(self):
        return list(self._convert_to_yfinance_ticker.values())

    @property
    def reorder_yfinance_tickers(self):
        return self._reorder_yfinance_tickers

    def rofex_instruments_by_underlier(self):
        return copy.deepcopy(self._pyrofex_future_underlier)

    def rofex_instruments_by_maturity(self):
        return copy.deepcopy(self._pyrofex_future_maturity)

    def rofex_instruments_by_ticker(self):
        return self._rofex_instruments_by_ticker.copy()

    def _parse_rofex(self):
        """
        Parsea los instrumentos de rofex y los guarda en un diccionario.
        """
        futures_regex = {ticker: re.compile(ticker) for ticker in self._tickers}
        pyrofex_instruments = wrapper.APIWrapper().get_detailed_instruments()
        for instrument in pyrofex_instruments["instruments"]:
            for ticker, regexp in futures_regex.items():
                if regexp.match(instrument["instrumentId"]["symbol"]):
                    rofex_ticker = instrument["instrumentId"]["symbol"]
                    maturity_date = parse(instrument["maturityDate"])
                    future_contract_size = instrument["contractMultiplier"]
                    future = FutureContract(
                        rofex_ticker, ticker, maturity_date, future_contract_size
                    )
                    self._pyrofex_future_underlier[ticker].append(future)
                    self._pyrofex_future_maturity[
                        rofex_ticker.replace(ticker, "")
                    ].append(future)
                    self._rofex_instruments_by_ticker[rofex_ticker] = future
