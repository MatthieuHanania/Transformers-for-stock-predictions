def one_buy_strategy(strategy, cash, last_price, quantity, probability, sentiment):
    if strategy.last_trade is None and quantity > 0:
        order = strategy.create_order(
            strategy.symbol,
            quantity,
            "buy",
            type="bracket",
            take_profit_price=last_price * 1.20,
            stop_loss_price=last_price * 0.95,
        )
        strategy.submit_order(order)
        strategy.last_trade = "buy"
        strategy.quantity_long += quantity


def buy_sell_sentiment_strategy(strategy, cash, last_price, quantity, probability, sentiment):
    if cash > last_price and quantity > 0:
        if sentiment == "positive" and probability > 0.999:
            if strategy.last_trade == "sell":
                strategy.sell_all()

            order = strategy.create_order(
                strategy.symbol,
                quantity,
                "buy",
                type="market",
            )
            strategy.submit_order(order)
            strategy.last_trade = "buy"
            strategy.quantity_long += quantity

        elif sentiment == "negative" and probability > 0.999:
            if strategy.last_trade == "buy":
                strategy.sell_all()

            # Avoid starting with a sell order when holding no long position
            if strategy.quantity_long > 1:
                order = strategy.create_order(
                    strategy.symbol,
                    quantity,
                    "sell",
                    type="market",
                )
                strategy.submit_order(order)
                strategy.last_trade = "sell"
                strategy.quantity_long -= quantity


def short_long_sentiment_strategy(strategy, cash, last_price, quantity, probability, sentiment):
    if cash > last_price and quantity > 0:
        if sentiment == "positive" and probability > 0.999:
            if strategy.last_trade in ("sell", "sell_short"):
                strategy.sell_all()

            order = strategy.create_order(
                strategy.symbol,
                quantity,
                "buy",
                type="bracket",
                take_profit_price=last_price * 1.20,
                stop_loss_price=last_price * 0.95,
            )
            strategy.submit_order(order)
            strategy.last_trade = "buy"
            strategy.quantity_long += quantity

        elif sentiment == "negative" and probability > 0.999:
            if strategy.last_trade == "buy":
                strategy.sell_all()

            order = strategy.create_order(
                strategy.symbol,
                quantity,
                "sell",
                type="bracket",
                take_profit_price=last_price * 0.80,
                stop_loss_price=last_price * 1.05,
            )
            strategy.submit_order(order)
            strategy.last_trade = "sell_short"
            strategy.quantity_long -= quantity
