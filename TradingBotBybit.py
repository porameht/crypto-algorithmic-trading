from time import sleep
from rich import print
from AccountInfoDisplayer import AccountInfoDisplayer
from Bybit import Bybit
from datetime import datetime, time
import pytz

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
        self.last_order_times = {}
        self.thai_tz = pytz.timezone('Asia/Bangkok')

    def is_trading_time(self):
        current_time = datetime.now(self.thai_tz).time()
        start_time = time(20, 0)  # 20:00
        end_time = time(6, 0)    # 06:00

        if start_time < end_time:
            return start_time <= current_time <= end_time
        else:  # Crosses midnight
            return current_time >= start_time or current_time <= end_time

    def execute_trades(self, positions):
        for elem in self.symbols:
            if len(positions) >= self.max_positions:
                break

            last_order_time = self.last_order_times.get(elem)
            
            if last_order_time:
                continue
            
            try:
                signal, take_profit, stop_loss = self.signal_func(self.session, elem, self.timeframe)
                if signal == 'up' and elem not in positions:
                    self.session.place_order_market(elem, 'buy', self.mode, self.leverage, self.qty, take_profit, stop_loss)
                    positions.append(elem)
                    sleep(1)
                elif signal == 'down' and elem not in positions:
                    self.session.place_order_market(elem, 'sell', self.mode, self.leverage, self.qty, take_profit, stop_loss)
                    positions.append(elem)
                    sleep(1)
            except Exception as err:
                print(f"Error executing trade for {elem}: {err}")

    def run(self):
        while True:
            if not self.is_trading_time():
                print("Outside trading hours. Waiting...")
                sleep(300)  # Sleep for 5 minutes before checking again
                continue

            balance = self.session.get_balance()
            self.last_order_times = self.session.get_last_order_time(last_hours=1)
            net_profit = self.session.get_net_profit(last_hours=12)

            if balance is None or self.symbols is None:
                print('❌ Cannot connect to Bybit')
                sleep(120)
                continue
            
            if net_profit > 0.3:
                print(f'🎉 Net profit in the last 12 hours: {net_profit} USDT')
                sleep(30)
                continue
            
            self.displayer.display_account_info(self.session, self.signal_func.__name__, self.timeframe)

            try:
                positions = self.session.get_positions(200)
                self.execute_trades(positions)
            except Exception as err:
                print(f"Error in main loop: {err}")
                sleep(60)

            print(f'🔎 Process Scanning... {len(self.symbols)} Charts => 🧠 {self.signal_func.__name__} signal')
            sleep(20)
