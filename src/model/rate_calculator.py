import copy
from collections import defaultdict


class ImplicitRateCalculator:
    """
    Calcula la tasa implicita
    """

    DAYS_IN_A_YEAR = 365

    def __init__(self, pyrofex_api, yfinance_api, tradeable_check):
        self._tradeable_underliers_futures = (
            tradeable_check.tradeable_pyrofex_future_underlier_ticker()
        )
        self._tradeable_tickers_maturities = tradeable_check.tradeable_ticker_maturity()
        self._pyrofex_api = pyrofex_api
        self._yfinance_api = yfinance_api
        self._buy_rate = defaultdict(dict)
        self._sell_rate = defaultdict(dict)

    def buy_rate(self):
        return copy.deepcopy(self._buy_rate)

    def sell_rate(self):
        return copy.deepcopy(self._sell_rate)

    def max_buy_rate(self, tradeable_maturity):
        return max(self._buy_rate[tradeable_maturity].items(), key=lambda x: x[1])

    def min_sell_rate(self, tradeable_maturity):
        return min(self._sell_rate[tradeable_maturity].items(), key=lambda x: x[1])

    def ready(self):
        return self._buy_rate and self._sell_rate

    def maturiry_ready_to_trade(self, tradeable_maturity):
        return (
            self._buy_rate[tradeable_maturity] and self._sell_rate[tradeable_maturity]
        )

    def _implicit_rate(self, maturity_price, current_price, time_to_expire):
        """
        TNA = ((1 + Tasa de cambio)^(1/DIAS_DEL_AÑO) - 1))*DIAS_DEL_AÑO
        """
        return (
            (maturity_price / current_price) ** (1 / time_to_expire) - 1
        ) * self.DAYS_IN_A_YEAR

    def update_rates(self):
        """
        Actualiza las tasas y ordena los instrumentos por fecha de vencimiento.
        """
        last_price_underlier = self._yfinance_api.last_prices()
        rofex_instruments_bids = self._pyrofex_api.bids()
        rofex_instruments_ask = self._pyrofex_api.asks()
        # self._buy_rate = defaultdict(dict)
        # self._sell_rate = defaultdict(dict)
        for ticker, last_price_of_each in last_price_underlier.items():
            for future in self._tradeable_underliers_futures[ticker]:
                future_ticker = future.ticker
                time_to_expire = future.time_to_expire()
                tradeable_maturity = self._tradeable_tickers_maturities[future_ticker]
                if future_ticker in rofex_instruments_bids:
                    self._buy_rate[tradeable_maturity][
                        future_ticker
                    ] = self._implicit_rate(
                        rofex_instruments_bids[future_ticker].price,
                        last_price_of_each,
                        time_to_expire,
                    )
                if future_ticker in rofex_instruments_ask:
                    self._sell_rate[tradeable_maturity][
                        future_ticker
                    ] = self._implicit_rate(
                        rofex_instruments_ask[future_ticker].price,
                        last_price_of_each,
                        time_to_expire,
                    )
