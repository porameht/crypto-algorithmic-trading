from abc import ABC, abstractmethod

class NotificationInterface(ABC):
    @abstractmethod
    def send_message(self, message: str) -> None:
        pass
    
    @abstractmethod
    def send_trade_message(self, 
                          symbol: str, 
                          side: str, 
                          entry: float, 
                          tp: float, 
                          sl: float, 
                          algorithm: str) -> None:
        pass 