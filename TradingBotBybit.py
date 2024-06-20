import os
from time import sleep
from rich import print
from AccountInfoDisplayer import AccountInfoDisplayer
from Bybit import Bybit

class TradingBotBybit:
    def __init__(self, session_config):
        self.session = Bybit(session_config['api'], session_config['secret'], session_config['accountType'])
        self.displayer = AccountInfoDisplayer()
        self.symbols = self.session.get_tickers()

        self.mode = session_config['mode']
        self.leverage = session_config['leverage']
        self.timeframe = session_config['timeframe']
        self.qty = session_config['qty']
        self.max_positions = session_config['max_positions']
        self.signal_func = session_config['signal_func']
        self.title = session_config['title']

    def execute_trades(self, positions):
        for elem in self.symbols:
            try:
                signal, take_profit, stop_loss = self.signal_func(self.session, elem, self.timeframe)
                if signal == 'up' and elem not in positions:
                    self.session.place_order_market(elem, 'buy', self.mode, self.leverage, self.qty, take_profit, stop_loss)
                    sleep(1)
                elif signal == 'down' and elem not in positions:
                    self.session.place_order_market(elem, 'sell', self.mode, self.leverage, self.qty, take_profit, stop_loss)
                    sleep(1)
            except Exception as err:
                print(f"Error executing trade for {elem}: {err}")

    def run(self):
        print('Bot is running...')
        while True:
            balance = self.session.get_balance()

            if balance is None or self.symbols is None:
                print('❌ Cannot connect')
                sleep(120)
                continue

            self.displayer.display_account_info(self.session, self.title, self.timeframe)

            try:
                positions = self.session.get_positions(200)
                if len(positions) >= self.max_positions:
                    break

                self.execute_trades(positions)

            except Exception as err:
                print(f"Error in main loop: {err}")
                sleep(60)

            print(f'🔎 Process Scanning... {len(self.symbols)} Charts')
            sleep(20)
