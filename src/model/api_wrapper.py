import json
import pyRofex


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class APIWrapper(metaclass=Singleton):
    """
    Para asegurar que solo una instancia de PyRofex sea creada.
    """

    with open(
        "C:/Users/54112/source/repos/Arbitraje-de-Tasas/src/conf/config.json"
    ) as f:
        config = json.load(f)

    def __init__(
        self,
        user=config["USER"],
        password=config["PASS"],
        account=config["ACCOUNT"],
        environment=pyRofex.Environment.REMARKET,
    ):
        self._environment = environment
        pyRofex.initialize(
            user=user, password=password, account=account, environment=self._environment
        )

    def __getattr__(self, attribute):
        return getattr(pyRofex, attribute)

    def close_websocket_connection_safely(self):
        try:
            pyRofex.close_websocket_connection(self._environment)
        except AttributeError:
            pass

    def __del__(self):
        self.close_websocket_connection_safely()
