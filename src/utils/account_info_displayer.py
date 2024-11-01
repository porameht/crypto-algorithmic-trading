from typing import List
from datetime import datetime
import pytz
from ..core.interfaces.exchange_interface import ExchangeInterface
from ..core.interfaces.notification_interface import NotificationInterface

class AccountInfoDisplayer:
    def __init__(self,
                 exchange: ExchangeInterface,
                 notifier: NotificationInterface,
                 title: str = "",
                 timeframe: str = "",
                 strategy_names: List[str] = None,
                 enable_logging: bool = True):
        self.exchange = exchange
        self.notifier = notifier
        self.title = title
        self.timeframe = timeframe
        self.strategy_names = strategy_names or []
        self.enable_logging = enable_logging
        
    def display_account_info(self) -> None:
        try:
            balance = self.exchange.get_balance()
            positions = self.exchange.get_positions()
            net_profit = self.exchange.get_net_profit(last_hours=12)
            
            message = self._format_account_info(
                balance, positions, net_profit)
                
            if self.enable_logging:
                print(message)
            self.notifier.send_message(message)
            
        except Exception as e:
            error_msg = f"Error displaying account info: {str(e)}"
            print(error_msg)
            self.notifier.send_message(f"❌ {error_msg}")
            
    def _format_account_info(self, 
                           balance: float,
                           positions: List[dict],
                           net_profit: float) -> str:
        bangkok_tz = pytz.timezone('Asia/Bangkok')
        current_time = datetime.now(bangkok_tz)
        
        header = (
            f"💰 Account Info {self.title} 💰\n"
            f"🕒 {current_time.strftime('%Y-%m-%d %H:%M:%S')} (Bangkok)\n"
            f"📊 Timeframe: {self.timeframe}\n"
            f"🤖 Strategies: {', '.join(self.strategy_names)}\n\n"
        )
        
        balance_info = (
            f"💵 Balance: {balance:.2f} USDT\n"
            f"📈 Net Profit (12h): {net_profit:.2f} USDT\n\n"
        )
        
        positions_info = "📍 Open Positions:\n"
        if positions:
            for pos in positions:
                positions_info += (
                    f"- {pos['symbol']}: {pos['side']} @ {pos['avgPrice']:.4f}\n"
                    f"  Size: {pos['size']:.4f}\n"
                    f"  TP: {pos['takeProfit']:.4f if pos['takeProfit'] else 'None'}\n"
                    f"  SL: {pos['stopLoss']:.4f if pos['stopLoss'] else 'None'}\n"
                )
        else:
            positions_info += "No open positions\n"
            
        return header + balance_info + positions_info 