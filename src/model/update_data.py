class DataUpdate:
    """
    Realiza seguimiento a la actualización de los datos
    """

    def __init__(self, yfinance_api, pyrofex_api):
        self._yfinance_api = yfinance_api
        self._pyrofex_api = pyrofex_api
        self._last_update = 0.0

    def update_boolean(self):
        "Devuelve True cuando los datos están por delante de la última vez que se leyeron"
        return (
            self._last_update < self._pyrofex_api.last_update_api()
            or self._last_update < self._yfinance_api.last_update_api()
        )

    def give_last_update(self):
        "Devuelve la última vez que se leyeron los datos"
        self._last_update = max(
            self._pyrofex_api.last_update_api(), self._yfinance_api.last_update_api()
        )
