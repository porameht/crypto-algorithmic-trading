import requests
from ..core.interfaces.notification_interface import NotificationInterface
from ..core.enums.trading_enums import OrderSide

class TelegramNotifier(NotificationInterface):
    def __init__(self, bot_token: str, group_id: str):
        self.bot_token = bot_token
        self.group_id = group_id
        
    def send_message(self, message: str) -> None:
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": self.group_id,
                "text": message,
                "parse_mode": "HTML"
            }
            requests.post(url, data=data)
        except Exception as e:
            print(f"Error sending telegram message: {e}")
            
    def send_trade_message(self, 
                          symbol: str, 
                          side: str, 
                          entry: float, 
                          tp: float, 
                          sl: float, 
                          algorithm: str) -> None:
        emoji = "🟢" if side == OrderSide.BUY.value else "🔴"
        message = (
            f"<b>🚀 New {side} Position 🚀</b>\n"
            f"<b>🤖 Algo:</b> <code>{algorithm}</code>\n\n"
            f"<b>{emoji} {symbol}</b>\n"
            f"<b>💰 Entry:</b> <code>{entry}</code>\n"
            f"<b>📊 Side:</b> <code>{side}</code>\n"
            f"<b>🎯 TP:</b> <code>{tp}</code>\n"
            f"<b>⛔ SL:</b> <code>{sl}</code>\n"
        )
        self.send_message(message) 