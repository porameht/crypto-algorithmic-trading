from abc import ABC, abstractmethod
from typing import Tuple, Optional
from ..enums.trading_enums import Signal

class StrategyInterface(ABC):
    @abstractmethod
    def generate_signal(self, 
                       exchange: 'ExchangeInterface', 
                       symbol: str, 
                       timeframe: str) -> Tuple[Signal, Optional[float], Optional[float]]:
        """
        Generate trading signal for given symbol
        Returns: (signal, take_profit, stop_loss)
        """
        pass 