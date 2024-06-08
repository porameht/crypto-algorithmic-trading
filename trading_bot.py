import random
from Bybit import Bybit
from time import sleep
import os
from tqdm import tqdm
from rich import print
from yaspin import yaspin
from dotenv import load_dotenv
load_dotenv()
# Import indicator functions
from indicators.adjust_take_profit_stop_loss import adjust_take_profit_stop_loss
from indicators.combined_rsi_macd_signal import combined_rsi_macd_signal
from indicators.rsi_basic_signal import rsi_basic_signal
from indicators.rsi_signal_14 import rsi_signal_14
from indicators.candlestick_ema_signal import candlestick_ema_signal
from indicators.williams_r_signal import williams_r_signal
from indicators.macd_ema_signal import macd_ema_signal
from indicators.ema_crossover_signal import ema_crossover_signal
from indicators.stochastic_rsi_signal import stochastic_rsi_signal

from indicators.combined.combined_trading_signal import combined_trading_signal

# Retrieve API credentials from environment variables
api = os.getenv('API_BYBIT', None)
secret = os.getenv('SECRET_BYBIT', None)
accountType = os.getenv('ACCOUNT_TYPE', None)

# Initialize Bybit session
session = Bybit(api, secret, accountType)

# Trading parameters
mode = 1  # 1 - Isolated, 0 - Cross
leverage = 10  # 10x
timeframe = 15  # 15 minutes
timeframes = [15]
qty = 1  # Amount of USDT for one order
max_positions = 50  # max 50 positions

# Get the list of symbols
symbols = session.get_tickers()

# Main bot function
def run_bot():
    print('Bot is running...')
    while True:
        balance = session.get_balance()
        
        if balance is None or symbols is None:
            print('❌ Cant connect')
            sleep(120)
        else:
            print(f'💰 Account balance: {balance} USDT')
            print(f'⏱️  Timeframe: {timeframe} minutes')
            try:
                positions = session.get_positions(200)
                print(f'📂 Opened positions: {len(positions)}')
                last_pnl = session.get_last_pnl(100)
                print(f'💰 Last 100 P&L: {last_pnl} USDT')
                current_pnl = session.get_current_pnl()
                print(f'💹 Current P&L: {current_pnl} USDT')
                for i, elem in enumerate(symbols, start=1):
                    if len(positions) >= max_positions:
                        break

                    with yaspin(text=f'Scanning {i} Signal {elem}... ', color="yellow") as spinner:
                        final_signal = combined_trading_signal(session, elem, timeframe)

                    print(f'🔍 Scan No.{i} Signal {elem}...')
                    if final_signal == 'up' and elem not in positions:
                        print(f'✅ Found BUY signal for {elem}')
                        kl = session.klines(elem, timeframe)
                        tp, sl = adjust_take_profit_stop_loss(kl)
                        session.place_order_market(elem, 'buy', mode, leverage, qty, tp, sl)
                        sleep(1)
                    if final_signal == 'down' and elem not in positions:
                        print(f'✅ Found SELL signal for {elem}')
                        kl = session.klines(elem, timeframe)
                        tp, sl = adjust_take_profit_stop_loss(kl)
                        session.place_order_market(elem, 'sell', mode, leverage, qty, tp, sl)
                        sleep(1)

            except Exception as err:
                print(err)
                print('No connection')
                for _ in tqdm(range(60, 0, -1)):
                    sleep(1)

        for _ in tqdm(range(100, 0, -5)):
            sleep(1)

if __name__ == "__main__":
    run_bot()