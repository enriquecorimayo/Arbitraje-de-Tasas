# Arbitraje-de-Tasas

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
    
### src api

Ahi se encuentra el archivo que corre el bot.

### test model

Contiene dos unit tets:

    - test_rate_calculator: contiene tres tests. 
    
        - controla que cuando existe arbitraje la tasa colocadora sea mayor a la tomadora.
        - contorla que cuando no existe arbitraje la tasa colocadora sea menor a la tomadora.
        - testea que el precio obtenido apartir de una tasa implícita conocida, cuando entra como input del modelo de la misma tasa.
        
    - test_strategy: contiene dos test.
    
        - testea que si no hay oportunidad, la estrategia no haga nada.
        ![image](https://user-images.githubusercontent.com/71297400/153792707-91c63b49-b223-40d2-8243-9d0a13ea96da.png)

        - testea que si hay oportunidad la estrategia opere los 4 instrumentos para generar el arbitraje.
        ![image](https://user-images.githubusercontent.com/71297400/153792811-99321196-da5d-4b81-9357-30027912bf95.png)



    
