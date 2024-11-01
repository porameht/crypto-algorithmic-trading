from typing import List, Dict
from ..core.enums.trading_enums import Signal
from .base_bot import BaseBot

class TradingBot(BaseBot):
    def execute_trades(self, positions: List[str]) -> None:
        """Execute trading logic for all strategies"""
        if len(positions) >= self.max_positions:
            return
            
        for symbol in self.exchange.get_symbols():
            if symbol in positions:
                continue
                
            try:
                for strategy in self.strategies:
                    signal, tp, sl = strategy.generate_signal(
                        self.exchange, symbol, self.timeframe)
                    
                    if signal and tp and sl:
                        success = self.exchange.place_order_market(
                            symbol, signal.value, self.mode, 
                            self.leverage, self.qty, tp, sl)
                            
                        if success:
                            self.notifier.send_trade_message(
                                symbol, signal.value,
                                self.exchange.get_last_price(symbol),
                                tp, sl, strategy.__class__.__name__)
                            return
                            
            except Exception as e:
                self.logger.error(f"Error executing trade for {symbol}: {e}")
                self.notifier.send_message(
                    f"❌ Error executing trade for {symbol}: {e}") 