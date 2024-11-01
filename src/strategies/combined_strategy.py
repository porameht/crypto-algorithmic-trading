from typing import List, Tuple, Optional
from ..core.interfaces.exchange_interface import ExchangeInterface
from ..core.enums.trading_enums import Signal
from .base_strategy import BaseStrategy

class CombinedStrategy(BaseStrategy):
    def __init__(self, strategies: List[BaseStrategy]):
        self.strategies = strategies
        
    def generate_signal(self, 
                       exchange: ExchangeInterface, 
                       symbol: str, 
                       timeframe: str) -> Tuple[Signal, Optional[float], Optional[float]]:
        """
        Generate trading signal by combining multiple strategies
        Only generates a signal if all strategies agree
        """
        signals = []
        tps = []
        sls = []
        
        for strategy in self.strategies:
            signal, tp, sl = strategy.generate_signal(exchange, symbol, timeframe)
            if signal != Signal.NONE and tp and sl:
                signals.append(signal)
                tps.append(tp)
                sls.append(sl)
                
        if signals and all(s == signals[0] for s in signals):
            # All strategies agree on the signal
            avg_tp = sum(tps) / len(tps)
            avg_sl = sum(sls) / len(sls)
            return signals[0], avg_tp, avg_sl
            
        return Signal.NONE, None, None 