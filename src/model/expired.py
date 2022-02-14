class ExpiredInstrument(Exception):
    def __init__(self, instrument):
        expire_message = f"El instrumento expiró: {instrument.maturity_date}"
        super().__init__(expire_message)
