import os
from time import sleep
from rich import print
from Bybit import Bybit
from indicators.combined_rsi_macd_signal import combined_rsi_macd_signal
from indicators.display_account_info import display_account_info
from indicators.jim_simons import jim_simons_signal
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

# Load environment variables
api_main = os.getenv('API_BYBIT', None)
secret_main = os.getenv('SECRET_BYBIT', None)
accountType_main = os.getenv('ACCOUNT_TYPE', None)

api_worker1 = os.getenv('API_BYBIT_WORKER1', None)
secret_worker1 = os.getenv('SECRET_BYBIT_WORKER1', None)
accountType_worker1 = os.getenv('ACCOUNT_TYPE_WORKER1', None)

if not all([api_main, secret_main, accountType_main]):
    print("❌ Missing main account API credentials")
    exit(1)

if not all([api_worker1, secret_worker1, accountType_worker1]):
    print("❌ Missing worker1 account API credentials")
    exit(1)

# Initialize sessions
session_main = Bybit(api_main, secret_main, accountType_main)
session_worker1 = Bybit(api_worker1, secret_worker1, accountType_worker1)

# Bot configuration
mode = 1  # 1 - Isolated, 0 - Cross
leverage = 10  # 10x
timeframe = 5 
qty = 10  # Amount of USDT for one order
max_positions = 10  # Max 10 positions

# Retrieve symbols
symbols = session_main.get_tickers()

def execute_trades(session, signal_func, symbols, mode, leverage, qty, positions):
    for elem in symbols:
        if len(positions) >= max_positions:
            break
        try:
            signal, take_profit, stop_loss = signal_func(session, elem, timeframe)
            if signal == 'up' and elem not in positions:
                session.place_order_market(elem, 'buy', mode, leverage, qty, take_profit, stop_loss)
                sleep(1)
            elif signal == 'down' and elem not in positions:
                session.place_order_market(elem, 'sell', mode, leverage, qty, take_profit, stop_loss)
                sleep(1)
        except Exception as err:
            print(f"Error executing trade for {elem}: {err}")

def run_bot():
    print('Bot is running...')
    while True:
        balance_main = session_main.get_balance()

        if balance_main is None or symbols is None:
            print('❌ Cannot connect')
            sleep(120)
            continue

        display_account_info(session_main, "📊 Account Information Main", timeframe)
        display_account_info(session_worker1, "📊 Account Information Worker1", timeframe)

        try:
            positions_main = session_main.get_positions(200)
            positions_worker1 = session_worker1.get_positions(200)
            
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = [
                    executor.submit(execute_trades, session_main, jim_simons_signal, symbols, mode, leverage, qty, positions_main),
                    executor.submit(execute_trades, session_worker1, combined_rsi_macd_signal, symbols, mode, leverage, qty, positions_worker1)
                ]
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as err:
                        print(f"Error in thread execution: {err}")

        except Exception as err:
            print(f"Error in main loop: {err}")
            sleep(60)

        print(f'🔎 Process Scanning... {len(symbols)} Charts')
        sleep(20)

if __name__ == "__main__":
    run_bot()
