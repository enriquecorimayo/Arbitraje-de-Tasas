from src.model import tradingbot as bot


def main():

    tickers = ["PAMP", "YPFD", "GGAL", "DLR"]
    bot.TradingBot(tickers).start()

if __name__ == "__main__":
    main()
