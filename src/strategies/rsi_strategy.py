import pandas as pd
import pandas_ta as ta
from typing import Tuple, Optional
from ..core.interfaces.exchange_interface import ExchangeInterface
from ..core.enums.trading_enums import Signal
from .base_strategy import BaseStrategy

class RSIStrategy(BaseStrategy):
    def __init__(self, rsi_period: int = 14, 
                 rsi_overbought: float = 70, 
                 rsi_oversold: float = 30,
                 tp_percent: float = 0.02,
                 sl_percent: float = 0.01):
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        self.tp_percent = tp_percent
        self.sl_percent = sl_percent

    def generate_signal(self, 
                       exchange: ExchangeInterface, 
                       symbol: str, 
                       timeframe: str) -> Tuple[Signal, Optional[float], Optional[float]]:
        """Generate trading signals based on RSI crossovers"""
        df = self._get_klines(exchange, symbol, timeframe)
        if df is None or len(df) < self.rsi_period + 2:
            return Signal.NONE, None, None

        # Calculate RSI
        rsi = ta.rsi(df['close'], length=self.rsi_period)
        
        if len(rsi) < 2:
            return Signal.NONE, None, None

        current_rsi = rsi.iloc[-1]
        previous_rsi = rsi.iloc[-2]
        current_price = df['close'].iloc[-1]

        # Generate signals
        if previous_rsi < self.rsi_oversold and current_rsi > self.rsi_oversold:
            tp, sl = self._calculate_tp_sl(Signal.UP, current_price, 
                                         self.tp_percent, self.sl_percent)
            return Signal.UP, tp, sl
            
        elif previous_rsi > self.rsi_overbought and current_rsi < self.rsi_overbought:
            tp, sl = self._calculate_tp_sl(Signal.DOWN, current_price,
                                         self.tp_percent, self.sl_percent)
            return Signal.DOWN, tp, sl

        return Signal.NONE, None, None 