# Arbitraje-de-Tasas

La idea del ejercicio es determinar si hay ocasiones en las que la tasa colocadora (compra de la acción y venta
del futuro) es superior a la tasa tomadora (venta en corto de la acción y compra del
futuro). En caso de que sea así realizar las operaciones correspondientes para generar el arbitraje.

## Estructura

La estructura del proyecto es:


    ├── src
        ├── config
            ├── configuration json files
        ├── model
            ├── python clases
        ├── api
            ├── bot
    ├── test
        ├── model
            ├── unit test files
    ├── .gitignore
    ├── setup.py
    ├── LICENSE
    └── README.md
   
### src config:

Se encuentra un archivo json con los datos de remarkets y otras config como costo de transacciones.

### src model:

Se encuentran varios archivos de python con las clases que conforman el bot de trading:

    - api_wrapper: contiene la clase para asegurarse que solo una instancia de PyRofex sea creada. Para eso usa una metaclase Singleton.
    - display: imprime en la pantalla las tasas implicitas
    - expired: contiene la clase para ver si el instrumento expiró.
    - instrument_handler: tiene dos clases, FutureContract e InstrumentHandler. La primera se encarga de representar contratos futuros, la segunda se transforma el input con los nombres "crudos" de los tickers para que yfinance y pyrofex puedan rastrear los correspondientes intrumentos.
    - market_apis: conformado por tres clases, una padre y dos hijas. Las clases hijas se conectan con la data de mercado, piden, actualizan y en caso de la que se conecta con PyRofex tambien manda ordenes.
    - rate_calculator: contiene la clase encargada de calcular y actualizar la tasa implícita.
    - strategy: contiene la clase que dectecta oportunidades de arbitraje y manda ordenes.
    - tradeable_check: contiene la clase que detecta si los instrumentos son tradeables.
    - tradingbot: contiene la clase que instancia al resto, se encarga de correr el bot de arbitraje.
    - data_update: contiene la clase que trackea la ultima vez que se leyeron precios.
    
### src api:

Ahi se encuentra el archivo que corre el bot.

### test model:

Contiene dos unit tets:

    - test_rate_calculator: contiene tres tests. 
    
        - controla que cuando existe arbitraje la tasa colocadora sea mayor a la tomadora.
        - contorla que cuando no existe arbitraje la tasa colocadora sea menor a la tomadora.
        - testea que el precio obtenido apartir de una tasa implícita conocida, cuando entra como input del modelo de la misma tasa.
        
    - test_strategy: contiene dos test.
    
        - testea que si no hay oportunidad, la estrategia no haga nada.

            ...
            ----------------------------------------------------------------------
            Ran 3 tests in 0.136s

            OK

        - testea que si hay oportunidad la estrategia opere los 4 instrumentos para generar el arbitraje.
        
                    --- Informacion del Trade FEB22 ---
            Tasa a tomar:
            Comprar:      GGAL/FEB22   ->       10 @ 115.00
            Vender:     GGAL         ->   1000.0 @ 100.00
            Tasa Implícita: 0.347193
            Monto del Trade: 100000.00
            Recepción del trade:   {'order': {'clientId': 'test_order_id'}}
            Estado del Trade: UNITTEST
            ---
            Tasa a colocar:
            Vender:     PAMP/FEB22   ->       10 @ 120.00
            Comprar:      PAMP         ->   1000.0 @ 100.00
            Tasa Implícita: 0.452984
            Monto del Trade: 100000.00
            Recepción del trade:   {'order': {'clientId': 'test_order_id'}}
            Estado del Trade: UNITTEST
            --------------------------------------------
            Dif. de Tasas:     0.095791
            Posición Promedio: 100000.00
            --------------------------------------------

            ..
            ----------------------------------------------------------------------
            Ran 2 tests in 0.173s

            OK



    
