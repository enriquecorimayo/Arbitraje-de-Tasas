from src.model import tradingbot as bot


def main():

    underlier_update_frecuency = 0.5
    tickers = ["PAMP", "YPFD", "GGAL", "DLR"]
    bot.TradingBot(tickers, underlier_update_frecuency).start()


if __name__ == "__main__":
    main()
