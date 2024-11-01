from abc import ABC
from typing import Tuple, Optional, Dict
import pandas as pd
from ..core.interfaces.strategy_interface import StrategyInterface
from ..core.interfaces.exchange_interface import ExchangeInterface
from ..core.enums.trading_enums import Signal

class BaseStrategy(StrategyInterface, ABC):
    def _get_klines(self, 
                    exchange: ExchangeInterface,
                    symbol: str,
                    timeframe: str,
                    limit: int = 100) -> Optional[pd.DataFrame]:
        """Get historical klines/candlestick data"""
        try:
            klines = exchange.get_klines(symbol, timeframe, limit)
            if not klines:
                return None
                
            df = pd.DataFrame(klines)
            df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
            return df
            
        except Exception as e:
            print(f"Error getting klines for {symbol}: {e}")
            return None
            
    def _calculate_tp_sl(self, 
                        signal: Signal, 
                        current_price: float,
                        tp_percent: float = 0.02,
                        sl_percent: float = 0.01) -> Tuple[float, float]:
        """Calculate take profit and stop loss levels"""
        if signal == Signal.UP:
            tp = current_price * (1 + tp_percent)
            sl = current_price * (1 - sl_percent)
        else:  # Signal.DOWN
            tp = current_price * (1 - tp_percent)
            sl = current_price * (1 + sl_percent)
            
        return tp, sl 