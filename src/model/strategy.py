from collections import namedtuple
import json
import pyRofex


class Strategy:
    """
    Detecta oportunidades de arbitraje y manda ordenes.
    """

    def __init__(
        self,
        instrument_handler,
        implicit_rate_calculator,
        pyrofex_api,
        yfinance_api,
        data_update,
        tradeable_check,
    ):
        self._futures_by_ticker = instrument_handler.rofex_instruments_by_ticker()
        self._tradeable_maturitys = tradeable_check.tradeable_maturities()
        self._implicit_rate_calculator = implicit_rate_calculator
        self._pyrofex_api = pyrofex_api
        self._yfinance_api = yfinance_api
        self._data_update = data_update

    def start_trades(self):
        """Tradea cada vencimiento"""
        for tradeable_maturity in self._tradeable_maturitys:
            if self._implicit_rate_calculator.maturiry_ready_to_trade(
                tradeable_maturity
            ):
                self.start_trades_by_maturity(tradeable_maturity)

    def start_trades_by_maturity(self, tradeable_maturity):
        """Si hay oportunidades manda las ordenes"""
        # Vender tasa tomadora cara y comprar tasa colocadora barata.
        ticker_to_sell, max_buy_rate = self._implicit_rate_calculator.max_buy_rate(
            tradeable_maturity=tradeable_maturity
        )
        ticker_to_buy, min_sell_rate = self._implicit_rate_calculator.min_sell_rate(
            tradeable_maturity=tradeable_maturity
        )

        with open(
            "C:/Users/54112/source/repos/Arbitraje-de-Tasas/src/conf/config.json"
        ) as f:
            config = json.load(f)
        # Esto no es lo mejor, pero a fin de hacerlo sencillo, si la difrencia de la tasa cara con la barata
        # es menor a la al costo de transaccion, no ejecutar trade...
        # Se podría mejorar de la siguiente manera:
        # Si la diferencia entre el cashflow resultante de colocar tasa cara y tomar tasa barata
        # es mayor al costo de transaccion, entonces ejecutar trade.(Tener en cuenta que los montos
        # de buy y sell del spot no siempre coinciden por lo que es mejor hacerlo de esta manera...)
        if not max_buy_rate - min_sell_rate > config["COST"]:
            return
        # Si hay oportunidad de arbitrar determinar el size.
        future_to_buy = self._futures_by_ticker[ticker_to_buy]
        future_to_sell = self._futures_by_ticker[ticker_to_sell]
        # Precio del Spot
        underlier_to_buy = future_to_sell.underlier_ticker
        underlier_buy_price = self._yfinance_api.price(underlier_to_buy)
        underlier_to_sell = future_to_buy.underlier_ticker
        underlier_sell_price = self._yfinance_api.price(underlier_to_sell)

        rofex_instruments_ask = self._pyrofex_api.asks()
        rofex_instruments_bids = self._pyrofex_api.bids()
        available_buy_size = rofex_instruments_ask[ticker_to_buy].size
        available_sell_size = rofex_instruments_bids[ticker_to_sell].size
        # Minimo size entre sell y buy
        amount_to_trade = min(
            available_buy_size
            * future_to_buy.future_contract_size
            * underlier_sell_price,
            available_sell_size
            * future_to_sell.future_contract_size
            * underlier_buy_price,
        )
        # Redondear el size en unidad de contratos (HACER CON math.ceil... probar el lunes cuando abra el mercao)
        buy_size = int(
            amount_to_trade / future_to_buy.future_contract_size / underlier_sell_price
            + 0.5
        )
        sell_size = int(
            amount_to_trade / future_to_sell.future_contract_size / underlier_buy_price
            + 0.5
        )
        buy_price = rofex_instruments_ask[ticker_to_buy].price
        sell_price = rofex_instruments_bids[ticker_to_sell].price
        underlier_buy_size = sell_size * future_to_sell.future_contract_size
        underlier_sell_size = buy_size * future_to_buy.future_contract_size
        # Profit
        trade_rate_profit = max_buy_rate - min_sell_rate - config["COST"]
        av_position_to_take = (
            underlier_buy_size * underlier_buy_price
            + underlier_sell_size * underlier_sell_price
        ) * 0.5
        # Si no hay que actualizar data y hay size de buy y sell mandar orden.
        if not self._data_update.update_boolean() and (buy_size * sell_size) > 0:
            # No se puede mandar Market Order por Remarkets
            # Ponmos Limit order
            buy_order = self._pyrofex_api.place_order(
                ticker=ticker_to_buy,
                side=pyRofex.Side.BUY,
                size=buy_size,
                price=buy_price,
                time_in_force=pyRofex.TimeInForce.ImmediateOrCancel,
                order_type=pyRofex.OrderType.LIMIT,
            )
            sell_order = self._pyrofex_api.place_order(
                ticker=ticker_to_sell,
                side=pyRofex.Side.SELL,
                size=sell_size,
                price=sell_price,
                time_in_force=pyRofex.TimeInForce.ImmediateOrCancel,
                order_type=pyRofex.OrderType.LIMIT,
            )
            # Falta agregar las ordenes de los SPOT, pero de todas maneras no tienen ninguna liquidez en REMARKETS...
            trade_info = [
                f"--- Informacion del Trade {tradeable_maturity} ---",
                "Tasa a tomar:",
                f"Comprar:      {ticker_to_buy:<12} -> {buy_size:>8} @ {buy_price:.2f}",
                f"Vender:     {underlier_to_sell:<12} -> {underlier_sell_size:>8} @ {underlier_sell_price:.2f}",
                f"Tasa Implícita: {min_sell_rate:.6f}",
                f"Monto del Trade: {underlier_sell_size * underlier_sell_price:.2f}",
                f"Recepción del trade:   {buy_order}",
                f'Estado del Trade: {self._pyrofex_api.order_execution_status(buy_order["order"]["clientId"])}',
                f"---",
                f"Tasa a colocar:",
                f"Vender:     {ticker_to_sell:<12} -> {sell_size:>8} @ {sell_price:.2f}",
                f"Comprar:      {underlier_to_buy:<12} -> {underlier_buy_size:>8} @ {underlier_buy_price:.2f}",
                f"Tasa Implícita: {max_buy_rate:.6f}",
                f"Monto del Trade: {underlier_buy_size * underlier_buy_price:.2f}",
                f"Recepción del trade:   {sell_order}",
                f'Estado del Trade: {self._pyrofex_api.order_execution_status(sell_order["order"]["clientId"])}',
                f"--------------------------------------------",
                f"Dif. de Tasas:     {trade_rate_profit:.6f}",
                f"Posición Promedio: {av_position_to_take:.2f}",
                f"--------------------------------------------",
                "",
            ]

            print("\n".join(trade_info), flush=True)
