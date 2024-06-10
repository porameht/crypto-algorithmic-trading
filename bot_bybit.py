from Bybit import Bybit
from time import sleep
import os
from tqdm import tqdm
from yaspin import yaspin
from rich import print

from indicators.adjust_take_profit_stop_loss import adjust_take_profit_stop_loss
from indicators.rsi_basic_signal import rsi_basic_signal

api = os.getenv('API_BYBIT', None)
secret = os.getenv('SECRET_BYBIT', None)
accountType = os.getenv('ACCOUNT_TYPE', None)

session = Bybit(api, secret, accountType)

mode = 1  # 1 - Isolated, 0 - Cross
leverage = 10  # 10x
timeframe = 15 # 15 minutes
qty = 1 # Amount of USDT for one order
max_positions = 50 # max 10 positions

symbols = session.get_tickers()

def run_bot():
    print('Bot is running...')
    while True:
        balance = session.get_balance()
        if balance is None or symbols is None:
            print('❌ Cant connect')
            sleep(120)
        if balance is not None and symbols is not None:
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
                        signal = rsi_basic_signal(session, elem, timeframe, 20)
                    if signal == 'up' and not elem in positions:
                        print(f'✅ Found BUY signal for {elem}')
                        kl = session.klines(elem, timeframe)
                        tp, sl = adjust_take_profit_stop_loss(kl)
                        session.place_order_market(elem, 'buy', mode, leverage, qty, tp, sl)
                        sleep(1)
                    if signal == 'down' and not elem in positions:
                        print(f'✅ Found SELL signal for {elem}')
                        kl = session.klines(elem, timeframe)
                        tp, sl = adjust_take_profit_stop_loss(kl)
                        session.place_order_market(elem, 'sell', mode, leverage, qty, tp, sl)
                        sleep(1)

            except Exception as err:
                print(err)
                print('No connection')
                for i in tqdm(range(60, 0, -1)):
                    sleep(1)

        for i in tqdm(range(100, 0, -5)):
            sleep(1)            
            


if __name__ == "__main__":
    run_bot()