from StrategyEvaluator import StrategyEvaluator
from Strategies import Strategies

from Binance import Binance
from TradingModel import TradingModel
import sys
import json
import time
from decimal import Decimal, getcontext


# Now, We will put everything together. Continuing with our command line interface, we will allow ourselves
# to backtest strategies, evaluate them (see what coins have those strategies fulfilled right now), and if
# any coins are eligible, we will plot & backtest that strategy on that particular coin, and if we are
# happy with the results, we can place an order.

# We will update this function a little bit, to make it more customizable
def BacktestStrategies(symbols=[], interval='4h', plot=False, strategy_evaluators=[],
                       options=dict(starting_balance=100, initial_profits=1.01, initial_stop_loss=0.9,
                                    incremental_profits=1.005, incremental_stop_loss=0.995)):
    coins_tested = 0
    trade_value = options['starting_balance']
    for symbol in symbols:
        print(symbol)
        model = TradingModel(symbol=symbol, timeframe=interval)
        for evaluator in strategy_evaluators:
            resulting_balance = evaluator.backtest(
                model,
                starting_balance=options['starting_balance'],
                initial_profits=options['initial_profits'],
                initial_stop_loss=options['initial_stop_loss'],
                incremental_profits=options['incremental_profits'],
                incremental_stop_loss=options['incremental_stop_loss'],
            )

            if resulting_balance != trade_value:
                print(evaluator.strategy.__name__
                      + ": starting balance: " + str(trade_value)
                      + ": resulting balance: " + str(round(resulting_balance, 2)))

                if plot:
                    model.plotData(
                        buy_signals=evaluator.results[model.symbol]['buy_times'],
                        sell_signals=evaluator.results[model.symbol]['sell_times'],
                        plot_title=evaluator.strategy.__name__ + " on " + model.symbol)

                evaluator.profits_list.append(resulting_balance - trade_value)
                evaluator.updateResult(trade_value, resulting_balance)

            coins_tested = coins_tested + 1

    for evaluator in strategy_evaluators:
        print("")
        evaluator.printResults()


# Now, We will write the function that checks the current market conditions
# & allows us to place orders if the conditions are good

# But First, We need to define the messages that the user will see:

strategy_matched_symbol = "\nStragey Matched Symbol! \
	\nType 'b' then ENTER to backtest the strategy on this symbol & see the plot \
	\nType 'p' then ENTER if you want to Place an Order \
	\nTyping anything else or pressing ENTER directly will skip placing an order this time.\n"

ask_place_order = "\nType 'p' then ENTER if you want to Place an Order \
	\nTyping anything else or pressing ENTER directly will skip placing an order this time.\n"


def EvaluateStrategies(symbols=[], strategy_evaluators=[], interval='1h',
                       options=dict(starting_balance=100, initial_profits=1.01, initial_stop_loss=0.9,
                                    incremental_profits=1.005, incremental_stop_loss=0.995)):
    for symbol in symbols:
        print(symbol, flush=True)

        model = TradingModel(symbol=symbol, timeframe=interval)
        for evaluator in strategy_evaluators:
            if evaluator.evaluate(model):
                print("\n" + evaluator.strategy.__name__ + " matched on " + symbol, flush=True)
0

                print("\nPlacing Buy Order. ")

                # We need to update the PlaceOrder function - we don't know what symbol we will be buying beforehand,
                # but let's say that we have received a symbol on coin ABCETH, where 1 ABC = 0.0034 ETH.
                # Binance only allows us to make orders ABOVE 0.01 ETH, so we need to buy at least 3 ABC.
                # However, if we received a symbol on XYZETH, and say 1 XYZ = 3 ETH, maybe we only want to buy 0.05 XYZ.
                # Therfore, we need to specify the amount we need to buy in terms of QUOTE ASSET (ETH), not base asset.
                # # We are changing the PlaceOrder function to reflect that.
                order_result = model.exchange.PlaceOrder(model.symbol, "BUY", "MARKET", quantity=0.02, test=True)
                if "code" in order_result:
                    print("\nERROR.")
                    print(order_result)
                    lf.write("order: ")

                else:
                    print("\nSUCCESS.")
                    print(order_result)
                    model.exchange.GetSymbolData("")
                #sys.exit("exiting program an order has been placed")



opening_text = "\nWelcome to Matthew's Crypto Trading Bot. \n \
	Press 'e' (ENTER) to execute trading strategy \n \
	Press 'q' (ENTER) to quit.  \n \
    \tPress 'CTRL + c' (ENTER) to stop trading"


def Main():
    #log file.. when bot is running in paper mode log trades
    lf = open('tradelog.txt', 'w')
    lf.write("welcoem to trade bot's log file")
    print(opening_text)
    answer = input()
    if answer == 'e':
        exchange = Binance()
        symbols = ["BNBETH"] #, "BTCUSDT", "BNBBTC", "LTCBTC", "BANDBTC", "ETHBTC"]    #exchange.GetTradingSymbols(quoteAssets=["ETH"])

        strategy_evaluators = [
            #StrategyEvaluator(strategy_function=Strategies.bollStrategy),
            #StrategyEvaluator(strategy_function=Strategies.maStrategy),
            StrategyEvaluator(strategy_function=Strategies.ichimokuBullish)
        ]
        #loop 20 times a second
        while True:
            try:
                t1 = time.monotonic()
                print(str(t1), flush=True)
                #BacktestStrategies(symbols=symbols, interval='5m', plot=True, strategy_evaluators=strategy_evaluators)
                EvaluateStrategies(symbols=symbols, interval='5m', strategy_evaluators=strategy_evaluators)
                t2 = time.monotonic()
                if (t2 - t1) < 0.05:
                    time.sleep(0.05)
            except KeyboardInterrupt:
                print("key board interrupt by user")
                return
    elif answer == 'q':
        sys.exit("user quit program")

    lf.close()





if __name__ == '__main__':
    Main()