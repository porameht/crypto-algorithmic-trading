import os
from time import sleep
from rich import print
from AccountInfoDisplayer import AccountInfoDisplayer
from Bybit import Bybit
from indicators.combined_rsi_macd_signal import combined_rsi_macd_signal
from indicators.jim_simons import jim_simons_signal
from concurrent.futures import ThreadPoolExecutor, as_completed

class TradingBotBybit:
    def __init__(self, config):
        self.config = config

        # Initialize sessions
        self.session_main = Bybit(config['api_main'], config['secret_main'], config['accountType_main'])
        self.session_worker1 = Bybit(config['api_worker1'], config['secret_worker1'], config['accountType_worker1'])
        self.displayer = AccountInfoDisplayer()

        # Retrieve symbols
        self.symbols = self.session_main.get_tickers()

    def execute_trades(self, session, signal_func, symbols, mode, leverage, qty, positions):
        for elem in symbols:
            if len(positions) >= self.config['max_positions']:
                break
            try:
                signal, take_profit, stop_loss = signal_func(session, elem, self.config['timeframe'])
                if signal == 'up' and elem not in positions:
                    session.place_order_market(elem, 'buy', mode, leverage, qty, take_profit, stop_loss)
                    sleep(1)
                elif signal == 'down' and elem not in positions:
                    session.place_order_market(elem, 'sell', mode, leverage, qty, take_profit, stop_loss)
                    sleep(1)
            except Exception as err:
                print(f"Error executing trade for {elem}: {err}")

    def run(self):
        print('Bot is running...')
        while True:
            balance_main = self.session_main.get_balance()

            if balance_main is None or self.symbols is None:
                print('❌ Cannot connect')
                sleep(120)
                continue

            self.displayer.display_account_info(self.session_main, "📊 Account Information Main", self.config['timeframe'])
            self.displayer.display_account_info(self.session_worker1, "📊 Account Information Worker1", self.config['timeframe'])

            try:
                positions_main = self.session_main.get_positions(200)
                positions_worker1 = self.session_worker1.get_positions(200)

                with ThreadPoolExecutor(max_workers=2) as executor:
                    futures = [
                        executor.submit(self.execute_trades, self.session_main, jim_simons_signal, self.symbols, self.config['mode'], self.config['leverage'], self.config['qty'], positions_main),
                        executor.submit(self.execute_trades, self.session_worker1, combined_rsi_macd_signal, self.symbols, self.config['mode'], self.config['leverage'], self.config['qty'], positions_worker1)
                    ]
                    for future in as_completed(futures):
                        try:
                            future.result()
                        except Exception as err:
                            print(f"Error in thread execution: {err}")

            except Exception as err:
                print(f"Error in main loop: {err}")
                sleep(60)

            print(f'🔎 Process Scanning... {len(self.symbols)} Charts')
            sleep(20)
