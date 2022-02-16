import copy
import sys
import threading
import time
import traceback
from collections import defaultdict, namedtuple
from pprint import pprint
import src.model.api_wrapper as wrapper

import pyRofex
import yfinance

ZERO_LIMIT = 1e-4

# Las instancias namedtuple son igual de eficientes en la memoria que las tuplas normales porque
# no tienen diccionarios por instancia. Cada tipo de namedtuple está representada por su propia clase,
# que es creada usando la función de fábrica namedtuple(). Los argumentos son nombre de la nueva clase y
# una cadena que contiene los nombres de los elementos.
# El OrderBook servirá para el Mock en el unittest.

OrderBook = namedtuple("OrderBook", "price size")


class ApiData:
    def __init__(self):
        self._last_update_api = 0.0
        self._start_request = False

    # Las clases base definidas por el usuario pueden generar NotImplementedError
    # para indicar que una subclase debe definir un método o comportamiento, simulando una interfaz.
    def request_market_data(self):
        raise NotImplementedError

    def start_request(self):
        return self._start_request

    def stop(self):
        self._start_request = False

    def last_update_api(self):
        return self._last_update_api

    def _update_last_update_api(self):
        self._last_update_api = time.time()


class YfinanceAPI(ApiData):
    """
    Pide Data a Yahoo Finance, se actualiza cada un periodo determinado
    """

    def __init__(self, instrument_handler, update_frequency, tradeable_check):
        super().__init__()
        self._tickers = tradeable_check.tradeable_yfinance_tickers()
        self._reorder_tickers = instrument_handler.reorder_yfinance_tickers
        self._update_frequency = update_frequency
        self._listening_thread = None
        self._prices = {}

    def _update_prices(self):
        """Pide data de Yahoo Finance"""
        while self._start_request:
            try:
                data = yfinance.download(
                    tickers=self._tickers, period="1d", interval="1d", progress=False
                )
                start = time.time()
                prices = data["Close"].to_dict(orient="records")[0]
                # Si la diferencia es mayor al limite de tolerancia, se actualiza
                if any(
                    (
                        price - self._prices.get(self._reorder_tickers[ticker], 0.0)
                        > ZERO_LIMIT
                    )
                    for ticker, price in prices.items()
                ):
                    self._prices = {
                        self._reorder_tickers[ticker]: price
                        for ticker, price in prices.items()
                    }
                    self._update_last_update_api()
                    print(f"Actualizada {self._prices}\n", flush=True)
                time.sleep(self._update_frequency)
            except Exception as e:
                traceback.print_exc()
                print(f"Excepcion ocurrio actualizando Yahoo Finance... terminando...")
                self.stop()

    def request_market_data(self):
        """Crea un hilo aparte para el request de Yahoo Finance"""
        print("Conectando...")
        self._listening_thread = threading.Thread(target=self._update_prices)
        self._start_request = True
        self._listening_thread.start()
        print("Comenzó!")

    def last_prices(self):
        return self._prices.copy()

    def price(self, ticker):
        return self._prices.get(ticker, 0.0)


class PyRofexApi(ApiData):
    """
    Clase para usar PyRofex, principales funciones:
    -Pedir Data
    -Actualizar Data
    -Mandar Ordenes
    """

    BIDS_OFFERS = [pyRofex.MarketDataEntry.BIDS, pyRofex.MarketDataEntry.OFFERS]

    def __init__(self, tradeable_check, subscribe_to_order_report=False):
        super().__init__()
        self._futures_ticker = tradeable_check.tradeable_rofex_futures_tickers()
        self._subscribe_to_order_report = subscribe_to_order_report
        self._pyrofex_wrapper = wrapper.APIWrapper()
        self._bids = {}
        self._asks = {}
        # lock es usado para evitar que se actualice la data de Rofex mientras se está actualizando
        self._bids_lock = threading.Lock()
        self._asks_lock = threading.Lock()

    def __str__(self):
        repr_str = ""
        all_tickers = set(self._bids.keys()).union(set(self._asks.keys()))
        for ticker in all_tickers:
            repr_str += (
                f"{ticker}: "
                f'{self._bids[ticker].get(pyRofex.MarketDataEntry.BIDS.value, "-")}'
                f'{self._asks[ticker].get(pyRofex.MarketDataEntry.OFFERS.value, "-")}'
            )
        return repr_str

    def _market_data_handler(self, message):
        """
        Maneja los mensajes de datos de mercado recibidos a través de websocket
        Analiza los datos y mantiene la información de oferta/demanda para cada ticker

        """
        try:
            print(f"Mensaje: Market Data de Rofex ... {message}\n", flush=True)
            ticker = message["instrumentId"]["symbol"]
            market_data = message["marketData"]
            if market_data[pyRofex.MarketDataEntry.OFFERS.value]:
                md_entry = market_data[pyRofex.MarketDataEntry.OFFERS.value][0]
                with self._asks_lock:
                    self._asks[ticker] = OrderBook(md_entry["price"], md_entry["size"])
            if market_data[pyRofex.MarketDataEntry.BIDS.value]:
                md_entry = market_data[pyRofex.MarketDataEntry.BIDS.value][0]
                with self._bids_lock:
                    self._bids[ticker] = OrderBook(md_entry["price"], md_entry["size"])
            self._update_last_update_api()
        except Exception as e:
            traceback.print_exc()
            print(
                f"Excepcion durante el manejo de Market Data de Rofex... terminando..."
            )
            self.stop()

    def _order_report_handler(self, message):
        print("============ Reporte de la Orden ==============")
        pprint(message)
        print("=========================================================")
        sys.stdout.flush()

    def _error_handler(self, message):
        print(f"Error de Rofex: {message}")
        self.stop()

    # Cambie message por e
    def _exception_handler(self, e):
        print(f"Excepción de Rofex: {e.message}")
        self.stop()

    def request_market_data(self):
        """Pide data de PyRofex"""
        print("Conectando...")
        self._start_request = True
        self._pyrofex_wrapper.init_websocket_connection(
            market_data_handler=self._market_data_handler,
            order_report_handler=self._order_report_handler,
            error_handler=self._error_handler,
            exception_handler=self._exception_handler,
        )
        self._pyrofex_wrapper.market_data_subscription(
            tickers=self._futures_ticker, entries=self.BIDS_OFFERS
        )
        # Poner suscribe como True para que se suscriba a los reportes de ordenes
        if self._subscribe_to_order_report:
            self._pyrofex_wrapper.order_report_subscription()
        print("Comenzó!")

    def stop(self):
        super().stop()
        self._pyrofex_wrapper.close_websocket_connection_safely()

    def asks(self):
        with self._asks_lock:
            copied = copy.deepcopy(self._asks)
        return copied

    def bids(self):
        with self._bids_lock:
            copied = copy.deepcopy(self._bids)
        return copied

    def place_order(self, *args, **kwargs):
        return self._pyrofex_wrapper.send_order(*args, **kwargs)

    def get_order_status(self, *args, **kwargs):
        return self._pyrofex_wrapper.get_order_status(*args, **kwargs)

    def order_execution_status(self, order_id):
        return self.get_order_status(order_id)["order"]["status"]
