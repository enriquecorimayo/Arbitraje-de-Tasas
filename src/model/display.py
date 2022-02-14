from tabulate import tabulate


class Display:
    """
    Muestra las tasas implicitas
    """

    EMPTY_ROW_STR = "*" * 12 + " -> " + "*" * 10

    def __init__(self, implicit_rate_calculator):
        self._implicit_rate_calculator = implicit_rate_calculator

    def print_implicit_rates(self):
        # Obitiene las tasas implicitas
        buy_rate = self._implicit_rate_calculator.buy_rate()
        sell_rate = self._implicit_rate_calculator.sell_rate()
        buy_rate_print = {
            tradeable_maturity: sorted(
                [(ticker, rate) for ticker, rate in values.items()], key=lambda x: x[1]
            )
            for tradeable_maturity, values in buy_rate.items()
        }
        sell_rate_print = {
            tradeable_maturity: sorted(
                [(ticker, rate) for ticker, rate in values.items()], key=lambda x: x[1]
            )
            for tradeable_maturity, values in sell_rate.items()
        }

        # Llenar las filas vacias con valores
        tradeable_maturitys = set(buy_rate.keys()).union(set(sell_rate.keys()))
        max_buyer_entries = max(len(entries) for entries in buy_rate_print.values())
        max_seller_entries = max(len(entries) for entries in buy_rate_print.values())
        rates_to_print = {}
        for tradeable_maturity in tradeable_maturitys:
            buyer_values = buy_rate_print.get(
                tradeable_maturity, [self.EMPTY_ROW_STR] * max_buyer_entries
            )
            rates_to_print[tradeable_maturity] = [self.EMPTY_ROW_STR] * (
                max_buyer_entries - len(buyer_values)
            ) + [f"{value[0]:<12} -> {value[1]:10.6f}" for value in buyer_values]
            seller_values = sell_rate_print.get(
                tradeable_maturity, [self.EMPTY_ROW_STR] * max_seller_entries
            )
            rates_to_print[tradeable_maturity] += ["+" * 26]
            rates_to_print[tradeable_maturity] += [
                f"{value[0]:<12} -> {value[1]:10.6f}" for value in seller_values
            ] + [self.EMPTY_ROW_STR] * (max_seller_entries - len(seller_values))
        table_str = "Tasas Actualizadas:\n" + tabulate(
            rates_to_print, headers="keys", stralign="center", tablefmt="psql"
        )
        print(table_str, flush=True)
