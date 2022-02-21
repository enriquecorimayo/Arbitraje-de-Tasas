### MODIFICACIONES:

Las modificaciones realizadas fueron:

- Mover la actualización de precios  de yfinance dentro del Market Data Handler de PyRofex.

- Instanciar las siguientes clases dentro del Market Data Handler:

      ImplicitRateCalculator: Actualiza las tasas implícitas
      
      Display: Imprime las tasas
      
      Strategy: Verifica que existan oportunidades de arbitraje
      
- De esta forma el market data handler se encargará de actualizar cuando haya novedades, imprimir tasas actualizadas y verificar oportunidades de Trade.

- En caso de existir oportunidad las órdenes se envían desde el Market Data Handler.

Los files con modificaciones son:

    bot.py:modificación menor, solo se quitó el parámetro de frecuencia de update.

    tradingbot.py: se modificaron algunos parámetros. Se quitó el while True cuando se hace el lunch del bot. 

    strategy.py: modificación en los dos métodos de la clase Strategy para que pueda funcionar de forma correcta dentro del handler.

    market_apis.py: modificación mayor, rearmar el código dentro de market_data_handler, se agregaron nuevos parámetros y métodos para la clase PyRofexApi, modificación ligera en el método de update_price de la clase YfinaceAPI.

    rate_calculator.py: modificación menor, se agregaron un par de parámetros para que funcione correctamente dentro del handler.

