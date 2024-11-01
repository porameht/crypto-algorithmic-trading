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
        message = f"""{emoji} New {side} Position
                    Algorithm: {algorithm}
                    Symbol: {symbol}
                    Entry: {entry}
                    TP: {tp}
                    SL: {sl}
                    """
        self.send_message(message)

# https://api.telegram.org/bot{self.bot_token}/getMe
# https://api.telegram.org/bot{self.bot_token}/getUpdates