from backtrader_bybit import BybitStore
import datetime as dt
import backtrader as bt
from rsi_backtest import MACDStrategy, RSIStrategy
from strategy import CombinedStrategy
import os
from dotenv import load_dotenv
load_dotenv()

# Retrieve API credentials
BYBIT_API_KEY = os.getenv('API_BYBIT', None)
BYBIT_API_SECRET = os.getenv('SECRET_BYBIT', None)
BYBIT_ACCOUNT_TYPE = os.getenv('ACCOUNT_TYPE', None)

if BYBIT_API_KEY == "BYBIT_API_KEY":
    print("Please fill BYBIT_API_KEY and BYBIT_API_SECRET values!")
    exit(1)

# Custom Analyzer to calculate win rate
class WinRateAnalyzer(bt.Analyzer):
    def __init__(self):
        self.total_trades = 0
        self.winning_trades = 0

    def notify_trade(self, trade):
        if trade.isclosed:
            self.total_trades += 1
            if trade.pnl > 0:
                self.winning_trades += 1

    def get_analysis(self):
        win_rate = (self.winning_trades / self.total_trades) * 100 if self.total_trades > 0 else 0
        return {
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'win_rate': win_rate
        }

# Backtrader setup
cerebro = bt.Cerebro(quicknotify=True)
cerebro.broker.setcash(2000)  # Setting initial cash
cerebro.broker.setcommission(commission=0.0015)  # Set the commission - 0.15%

coin_target = 'USDT'
symbol = 'BTC' + coin_target
symbol2 = 'ETH' + coin_target

accountType = BYBIT_ACCOUNT_TYPE
store = BybitStore(
    api_key=BYBIT_API_KEY,
    api_secret=BYBIT_API_SECRET,
    coin_target=coin_target,
    testnet=False,
    accountType=accountType,
)

# Historical data setup
timeframe = "15m"
from_date = dt.datetime.now() - dt.timedelta(days=365*3)
data = store.getdata(timeframe=bt.TimeFrame.Days, compression=1, dataname=symbol, start_date=from_date, LiveBars=False)
data2 = store.getdata(timeframe=bt.TimeFrame.Days, compression=1, dataname=symbol2, start_date=from_date, LiveBars=False)

cerebro.adddata(data)
cerebro.adddata(data2)

cerebro.addstrategy(RSIStrategy, coin_target=coin_target, timeframe=timeframe)
cerebro.addanalyzer(WinRateAnalyzer, _name='winrate')

results = cerebro.run()  # Launching the strategy

# Extract the analyzer
winrate_analyzer = results[0].analyzers.winrate
winrate_results = winrate_analyzer.get_analysis()

# Print results
print()
print("$" * 77)
print(f"Liquidation value of the portfolio: {cerebro.broker.getvalue()}")  # Liquidation value of the portfolio
print(f"Remaining available funds: {cerebro.broker.getcash()}")  # Remaining available funds
print(f"Total trades: {winrate_results['total_trades']}")
print(f"Winning trades: {winrate_results['winning_trades']}")
print(f"Win rate: {winrate_results['win_rate']:.2f}%")
print("$" * 77)
