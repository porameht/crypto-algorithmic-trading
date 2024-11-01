from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class ExchangeInterface(ABC):
    @abstractmethod
    def get_balance(self) -> float:
        pass
    
    @abstractmethod
    def get_positions(self, limit: int = 200) -> List[Dict]:
        pass
    
    @abstractmethod
    def place_order_market(self, 
                          symbol: str, 
                          side: str, 
                          mode: str, 
                          leverage: int, 
                          qty: float, 
                          take_profit: float, 
                          stop_loss: float) -> bool:
        pass
    
    @abstractmethod
    def get_last_price(self, symbol: str) -> float:
        pass
    
    @abstractmethod
    def get_last_order_time(self, last_hours: int = 1) -> Dict[str, datetime]:
        pass
    
    @abstractmethod
    def get_net_profit(self, last_hours: int = 12) -> float:
        pass 