# Arbitraje-de-Tasas
Arbitraje de Tasas

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
   
src config:

Se encuentra un archivo json con los datos de remarkets y otras config como costo de transacciones.

src model:

Se encuentran varios archivos de python con las clases que conforman el bot de trading:

    - api_wrapper: clase para asegurarse que solo una instancia de PyRofex sea creada. Para eso usa una metaclase Singleton.
    - display: imprime en la pantalla las tasas implicitas
    - expired: clase para ver si el instrumento expiró.
    - instrument_handler: tiene dos clases, FutureContract e InstrumentHandler. La primera se encarga de representar contratos futuros, la segunda se transforma el input con los nombres "crudos" de los tickers para que yfinance y pyrofex puedan rastrear los correspondientes intrumentos.
    - market_apis: conformado por tres clases, una padre y dos hijas. Las clases hijas se conectan con la data de mercado, piden, actualizan y en caso de la que se conecta con PyRofex tambien manda ordenes.
    - rate_calculator: clase encargada de calcular la tasa implícita:
        ((1 + Tasa de cambio)^(1/DIAS_DEL_AÑO) - 1))*DIAS_DEL_AÑO
    
