from src.model.instrument_handler import InstrumentHandler

class TradeableCheck(InstrumentHandler):
    """
    Clase para ver que los instrumentos son tradeables.
    """

    def __init__(self,tickers):
        super().__init__(tickers)

    def tradeable_maturities(self):
        return list(self.tradeable_futures_by_maturity().keys())

    def tradeable_futures_by_maturity(self):
        return {maturity: futures for maturity, futures in self._pyrofex_future_maturity.items()
                if len(futures) > 1}

    def tradeable_ticker_maturity(self):
        return {future.ticker: maturity
                for maturity, futures in self.tradeable_futures_by_maturity().items()
                for future in futures}

    def tradeable_rofex_futures(self):
        return sum(self.tradeable_futures_by_maturity().values(), [])

    def tradeable_rofex_futures_tickers(self):
        return [future._ticker for future in self.tradeable_rofex_futures()]

    def tradeable_pyrofex_future_underlier_ticker(self):
        tradeable_tickers = self.tradeable_rofex_futures_tickers()
        return {underlier: [future for future in futures if future.ticker in tradeable_tickers]
                for underlier, futures in self._pyrofex_future_underlier.items()}

    def tradeable_yfinance_tickers(self):
        return list(set(self._convert_to_yfinance_ticker[future._underlier_ticker]
                        for future in self.tradeable_rofex_futures()))