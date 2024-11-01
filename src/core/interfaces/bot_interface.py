from abc import ABC, abstractmethod
from typing import List, Dict

class BotInterface(ABC):
    @abstractmethod
    def run(self) -> None:
        """Main bot execution loop"""
        pass
    
    @abstractmethod
    def execute_trades(self, positions: List[str]) -> None:
        """Execute trading logic"""
        pass
    
    @abstractmethod
    def display_account_info(self) -> None:
        """Display account information"""
        pass 