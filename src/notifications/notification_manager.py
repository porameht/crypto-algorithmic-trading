from typing import List
from ..core.interfaces.notification_interface import NotificationInterface

class NotificationManager:
    def __init__(self, notifiers: List[NotificationInterface]):
        self.notifiers = notifiers
    
    def send_message(self, message: str) -> None:
        """Send message through all configured notifiers"""
        for notifier in self.notifiers:
            try:
                notifier.send_message(message)
            except Exception as e:
                print(f"Error sending message through {notifier.__class__.__name__}: {e}")
    
    def send_trade_message(self, 
                          symbol: str, 
                          side: str, 
                          entry: float, 
                          tp: float, 
                          sl: float, 
                          algorithm: str) -> None:
        """Send trade message through all configured notifiers"""
        for notifier in self.notifiers:
            try:
                notifier.send_trade_message(symbol, side, entry, tp, sl, algorithm)
            except Exception as e:
                print(f"Error sending trade message through {notifier.__class__.__name__}: {e}") 