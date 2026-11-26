from datetime import datetime, timedelta
import os

from alpaca_trade_api import REST
from dotenv import load_dotenv
from lumibot.backtesting import YahooDataBacktesting
from lumibot.brokers import Alpaca
from lumibot.strategies import Strategy
from lumibot.traders import Trader

from sentiment_analysis import get_news_sentiment
from strategies import (
    buy_sell_sentiment_strategy,
    one_buy_strategy,
    short_long_sentiment_strategy,
)

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_API_SECRET")
BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets/v2")
IS_PAPER = os.getenv("ALPACA_PAPER", "True").lower() in ("true", "1", "yes")

if not API_KEY or not API_SECRET:
    raise ValueError(
        "Missing Alpaca credentials. Copy .env.example to .env and set ALPACA_API_KEY and ALPACA_API_SECRET."
    )

ALPACA_CREDS = {
    "API_KEY": API_KEY,
    "API_SECRET": API_SECRET,
    "PAPER": IS_PAPER,
}

STRATEGIES = {
    "one_buy": one_buy_strategy,
    "buy_sell": buy_sell_sentiment_strategy,
    "short_long": short_long_sentiment_strategy,
}


class MLTrader(Strategy):
    def initialize(
        self,
        symbol: str = "SPY",
        cash_at_risk: float = 0.5,
        strategy_name: str = "short_long",
    ):
        self.symbol = symbol
        self.sleeptime = "24H"
        self.last_trade = None
        self.cash_at_risk = cash_at_risk
        self.strategy_name = strategy_name
        self.quantity_long = 0
        self.quantity_short = 0
        self.api = REST(key_id=API_KEY, secret_key=API_SECRET, base_url=BASE_URL)

    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quantity = round(cash * self.cash_at_risk / last_price, 0)
        return cash, last_price, quantity

    def get_dates(self):
        today = self.get_datetime()
        days_prior = today - timedelta(days=5)
        return today.strftime("%Y-%m-%d"), days_prior.strftime("%Y-%m-%d")

    def get_sentiment_news(self):
        today, days_prior = self.get_dates()
        news = self.api.get_news(
            symbol=self.symbol,
            start=days_prior,
            end=today,
        )
        headlines = [item.__dict__["_raw"]["headline"] for item in news]
        return get_news_sentiment(headlines)

    def on_trading_iteration(self):
        cash, last_price, quantity = self.position_sizing()
        probability, sentiment = self.get_sentiment_news()

        strategy_fn = STRATEGIES.get(self.strategy_name)
        if strategy_fn is None:
            raise ValueError(f"Unknown strategy '{self.strategy_name}'. Choose from: {list(STRATEGIES)}")

        strategy_fn(self, cash, last_price, quantity, probability, sentiment)


if __name__ == "__main__":
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2023, 12, 31)
    broker = Alpaca(ALPACA_CREDS)

    params = {
        "symbol": "SPY",
        "cash_at_risk": 0.5,
        "strategy_name": "short_long",
    }

    strategy = MLTrader(name="mlstrat", broker=broker, parameters=params)
    strategy.backtest(
        YahooDataBacktesting,
        start_date,
        end_date,
        parameters=params,
    )

    # Uncomment to run live/paper trading instead of backtesting:
    # trader = Trader()
    # trader.add_strategy(strategy)
    # trader.run_all()
