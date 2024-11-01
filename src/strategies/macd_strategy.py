import pandas as pd
import pandas_ta as ta
from typing import Tuple, Optional
from ..core.interfaces.exchange_interface import ExchangeInterface
from ..core.enums.trading_enums import Signal
from .base_strategy import BaseStrategy

class MACDStrategy(BaseStrategy):
    def __init__(self, 
                 fast_period: int = 12,
                 slow_period: int = 26,
                 signal_period: int = 9,
                 tp_percent: float = 0.02,
                 sl_percent: float = 0.01):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.tp_percent = tp_percent
        self.sl_percent = sl_percent

    def generate_signal(self, 
                       exchange: ExchangeInterface, 
                       symbol: str, 
                       timeframe: str) -> Tuple[Signal, Optional[float], Optional[float]]:
        """Generate trading signals based on MACD crossovers"""
        df = self._get_klines(exchange, symbol, timeframe)
        if df is None or len(df) < self.slow_period + self.signal_period:
            return Signal.NONE, None, None

        # Calculate MACD
        macd = ta.macd(df['close'], 
                      fast=self.fast_period,
                      slow=self.slow_period,
                      signal=self.signal_period)
        
        if len(macd) < 2:
            return Signal.NONE, None, None

        macd_line = macd['MACD_' + str(self.fast_period) + '_' + str(self.slow_period) + '_' + str(self.signal_period)]
        signal_line = macd['MACDs_' + str(self.fast_period) + '_' + str(self.slow_period) + '_' + str(self.signal_period)]

        current_price = df['close'].iloc[-1]
        
        # Check for crossovers
        if (macd_line.iloc[-2] < signal_line.iloc[-2] and 
            macd_line.iloc[-1] > signal_line.iloc[-1]):
            tp, sl = self._calculate_tp_sl(Signal.UP, current_price,
                                         self.tp_percent, self.sl_percent)
            return Signal.UP, tp, sl
            
        elif (macd_line.iloc[-2] > signal_line.iloc[-2] and 
              macd_line.iloc[-1] < signal_line.iloc[-1]):
            tp, sl = self._calculate_tp_sl(Signal.DOWN, current_price,
                                         self.tp_percent, self.sl_percent)
            return Signal.DOWN, tp, sl

        return Signal.NONE, None, None 