from time import sleep
from rich import print
from Bybit import Bybit
from datetime import datetime, time
import pytz
from common.enums import OrderSide, OrderType, MarginMode, TimeFrame, Signal
from TelegramBot import TelegramBot
from functools import lru_cache
from typing import List, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class TradingBotBybit:
    def __init__(self, session_config: dict) -> None:
        """Initialize TradingBotBybit with configuration settings.
        
        Args:
            session_config: Dictionary containing API credentials and trading parameters
        """
        self._init_session(session_config)
        self._init_trading_params(session_config)
        self._init_telegram(session_config)
        self._signal_func_names = ", ".join(f.__name__ for f in self.signal_funcs)

    def _init_session(self, session_config: dict) -> None:
        """Initialize Bybit trading session."""
        self.session = Bybit(
            session_config['api'], 
            session_config['secret'],
            session_config['accountType']
        )
        self.symbols = self.session.get_tickers()
        self.session_config = session_config

    def _init_trading_params(self, session_config: dict) -> None:
        """Initialize trading parameters from config."""
        self.mode = session_config['mode']
        self.leverage = session_config['leverage']
        self.timeframe = session_config['timeframe']
        self.qty = session_config['qty']
        self.max_positions = session_config['max_positions']
        self.signal_funcs = session_config['signal_funcs']
        self.last_order_times = {}

    def _init_telegram(self, session_config: dict) -> None:
        """Initialize timezone and telegram settings."""
        self.telegram = TelegramBot(session_config)

    @lru_cache(maxsize=1)
    def is_trading_time(self) -> bool:
        """Check if current time is within trading hours (20:00-06:00)."""
        current_time = datetime.now(self.thai_tz).time()
        start_time = time(20, 0)  # 20:00
        end_time = time(6, 0)    # 06:00

        if start_time < end_time:
            return start_time <= current_time <= end_time
        return current_time >= start_time or current_time <= end_time

    def _handle_trade_signal(
        self, 
        symbol: str, 
        signal: str, 
        take_profit: float,
        stop_loss: float, 
        positions: List[str], 
        signal_func: Any
    ) -> bool:
        """Handle individual trade signal and place order if conditions are met.
        
        Returns:
            bool: True if trade was executed successfully, False otherwise
        """
        if symbol in positions:
            return False

        side = OrderSide.BUY if signal == Signal.UP.value else OrderSide.SELL
        result = self.session.place_order_market(
            symbol, 
            side.value, 
            self.mode, 
            self.leverage, 
            self.qty, 
            take_profit, 
            stop_loss
        )
        
        if not result:
            return False
            
        positions.append(symbol)
        last_price = self.session.get_last_price(symbol)
        self.telegram.send_trade_message(
            symbol, 
            side.value, 
            last_price, 
            take_profit, 
            stop_loss, 
            signal_func.__name__
        )
        sleep(1)
        return True

    def execute_trades(self, positions: List[str]) -> None:
        """Execute trades based on signal functions for all symbols."""
        for symbol in self.symbols:
            if len(positions) >= self.max_positions:
                break

            if self.last_order_times.get(symbol):
                continue
            
            try:
                signal_results = self._calculate_signals(symbol)
                self._process_signals(symbol, signal_results, positions)
            except Exception as err:
                error_msg = f"❌ Error executing trade for {symbol}: {err}"
                logger.error(error_msg)
                self.telegram.send_message(error_msg)
                print(error_msg)

    def _calculate_signals(self, symbol: str) -> List[Tuple]:
        """Calculate signals for all signal functions.
        
        Returns:
            List of tuples containing (function, signal, take_profit, stop_loss)
        """
        signal_results = []
        for signal_func in self.signal_funcs:
            try:
                signal_data = signal_func(self.session, symbol, self.timeframe, config=self.session_config)
                signal_results.append((signal_func, *signal_data))
            except Exception as e:
                logger.debug(f"Signal calculation failed for {signal_func.__name__}: {e}")
                continue
        return signal_results

    def _process_signals(self, symbol: str, signal_results: List[Tuple], positions: List[str]) -> None:
        """Process calculated signals and execute trades if conditions are met."""
        for signal_func, signal, take_profit, stop_loss in signal_results:
            print(f"👨‍💻 {symbol} {signal_func.__name__} {signal}")
            if signal not in [Signal.UP.value, Signal.DOWN.value]:
                self.telegram.send_message(f"👨‍💻 {symbol} {signal_func.__name__} {signal}")
                continue
                
            if self._handle_trade_signal(symbol, signal, take_profit, stop_loss, positions, signal_func):
                break

    def _check_net_profit(self) -> bool:
        """Check if net profit exceeds threshold and notify if needed."""
        net_profit = self.session.get_net_profit(last_hours=12)
        if net_profit <= 0.5:
            return False
            
        message = f'🎉 Net profit in the last 12 hours: {net_profit} USDT'
        print(message)
        
        current_time = datetime.now(pytz.timezone('Asia/Bangkok')).time()
        if current_time.hour in [0, 12] and current_time.minute == 0:
            self.telegram.send_message(message)
            sleep(30)
        return True

    def _check_account_info_interval(self) -> None:
        """Check and display account info every 1 minute."""
        if 'interval' not in self.session_config:
            return
        
        interval = int(self.session_config['interval'])
        current_time = datetime.now(pytz.timezone('Asia/Bangkok')).time()
        print(f'interval: {interval}')
        print(f'current_time: {current_time}')
        print(f'self.current_time.hour % interval: {current_time.hour % interval}')
        print(f'self.current_time.minute <= 3: {current_time.minute <= 1}')
        if current_time.hour % interval == 0 and current_time.minute <= 1:
            self.display_and_notify_account_info()
            sleep(30)

    def run(self) -> None:
        """Main bot execution loop."""
        while True:
            try:
                if not self._check_connection():
                    continue
                
                # if self._check_net_profit():
                #     continue

                self._execute_trading_cycle()

            except Exception as err:
                error_msg = f"❌ Error in main loop: {err}"
                logger.error(error_msg)
                self.telegram.send_message(error_msg)
                print(error_msg)
                sleep(60)

    def _check_connection(self) -> bool:
        """Check if connection to Bybit is active."""
        balance = self.session.get_balance()
        self.last_order_times = self.session.get_last_order_time(last_hours=1)

        if balance is None or self.symbols is None:
            print('❌ Cannot connect to Bybit')
            sleep(120)
            return False
        return True

    def _execute_trading_cycle(self) -> None:
        """Execute one cycle of trading operations."""
        positions = self.session.get_positions(200)
        positions_symbols = [position['symbol'] for position in positions]
        logger.info(f'🔎 Process started: Scanning {len(self.symbols)} charts with {self._signal_func_names} signals')
        self.execute_trades(positions_symbols)
        logger.info(f'🔎 Process completed: {len(self.symbols)} charts scanned with {self._signal_func_names} signals')
        sleep(20)
