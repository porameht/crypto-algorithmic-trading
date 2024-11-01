import requests
from common.enums import OrderSide

class TelegramBot:
    def __init__(self, config):
        self.config = config
        self.group_id = config['telegram_group_id']
        self.bot_token = config['telegram_bot_token']
        
    def send_message(self, message: str):
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
            
    def send_trade_message(self, symbol, side, entry, tp, sl, algorithm):
        emoji = "🟢" if side == OrderSide.BUY.value else "🔴"
        message = (
            f"<b>🚀 New {side} Position 🚀</b>\n"
            f"<b>🧠 Algo:</b> <code>{algorithm}</code>\n\n"
            f"\n<b>{emoji} {symbol}</b>\n"
            f"<b>💵 Entry:</b> <code>{entry}</code>\n"
            f"<b>📊 Side:</b> <code>{side}</code>\n"
            f"<b>🎯 TP:</b> <code>{tp}</code>\n"
            f"<b>🛑 SL:</b> <code>{sl}</code>\n"
        )
        self.send_message(message)

# https://api.telegram.org/bot{self.bot_token}/getMe
# https://api.telegram.org/bot{self.bot_token}/getUpdates