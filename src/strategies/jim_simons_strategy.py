import pandas as pd
import pandas_ta as ta
from typing import Tuple, Optional
from ..core.interfaces.exchange_interface import ExchangeInterface
from ..core.enums.trading_enums import Signal
from .base_strategy import BaseStrategy

class JimSimonsStrategy(BaseStrategy):
    def __init__(self,
                 ema_period: int = 200,
                 rsi_period: int = 14,
                 stoch_period: int = 14,
                 tp_percent: float = 0.02,
                 sl_percent: float = 0.01):
        self.ema_period = ema_period
        self.rsi_period = rsi_period
        self.stoch_period = stoch_period
        self.tp_percent = tp_percent
        self.sl_percent = sl_percent

    def generate_signal(self, 
                       exchange: ExchangeInterface, 
                       symbol: str, 
                       timeframe: str) -> Tuple[Signal, Optional[float], Optional[float]]:
        """
        Generate trading signals based on multiple indicators:
        - EMA trend
        - RSI
        - Stochastic RSI
        """
        df = self._get_klines(exchange, symbol, timeframe)
        if df is None or len(df) < self.ema_period:
            return Signal.NONE, None, None

        # Calculate indicators
        ema = ta.ema(df['close'], length=self.ema_period)
        rsi = ta.rsi(df['close'], length=self.rsi_period)
        stoch = ta.stochrsi(df['close'], length=self.stoch_period)
        
        if len(ema) < 1 or len(rsi) < 1 or len(stoch) < 3:
            return Signal.NONE, None, None

        current_price = df['close'].iloc[-1]
        current_rsi = rsi.iloc[-1]
        
        stoch_k = stoch['STOCHRSIk_' + str(self.stoch_period)]
        stoch_d = stoch['STOCHRSId_' + str(self.stoch_period)]

        # Buy conditions
        buy_condition = (
            current_price > ema.iloc[-1] and  # Price above EMA
            current_rsi < 40 and              # RSI showing oversold
            stoch_k.iloc[-1] < 20 and        # StochRSI oversold
            stoch_k.iloc[-3] < stoch_d.iloc[-3] and
            stoch_k.iloc[-2] < stoch_d.iloc[-2] and
            stoch_k.iloc[-1] > stoch_d.iloc[-1]  # StochRSI crossover
        )

        # Sell conditions
        sell_condition = (
            current_price < ema.iloc[-1] and  # Price below EMA
            current_rsi > 60 and              # RSI showing overbought
            stoch_k.iloc[-1] > 80 and        # StochRSI overbought
            stoch_k.iloc[-3] > stoch_d.iloc[-3] and
            stoch_k.iloc[-2] > stoch_d.iloc[-2] and
            stoch_k.iloc[-1] < stoch_d.iloc[-1]  # StochRSI crossover
        )

        if buy_condition:
            tp, sl = self._calculate_tp_sl(Signal.UP, current_price,
                                         self.tp_percent, self.sl_percent)
            return Signal.UP, tp, sl
            
        elif sell_condition:
            tp, sl = self._calculate_tp_sl(Signal.DOWN, current_price,
                                         self.tp_percent, self.sl_percent)
            return Signal.DOWN, tp, sl

        return Signal.NONE, None, None 