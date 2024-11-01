import os
from typing import Dict, Any
from dotenv import load_dotenv

class ConfigLoader:
    @staticmethod
    def load_config() -> Dict[str, Any]:
        load_dotenv()
        
        config = {
            'api_main': os.getenv('API_BYBIT'),
            'secret_main': os.getenv('SECRET_BYBIT'),
            'accountType_main': os.getenv('ACCOUNT_TYPE'),
            'account_info_telegram_time': os.getenv('ACCOUNT_INFO_TELEGRAM_TIME'),
            'timeframe': os.getenv('TIMEFRAME', 30),
            'mode': os.getenv('MODE', 1),
            'leverage': int(os.getenv('LEVERAGE', 10)),
            'qty': float(os.getenv('QTY', 10)),
            'max_positions': int(os.getenv('MAX_POSITIONS', 10)),
            'telegram_bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
            'telegram_group_id': os.getenv('TELEGRAM_GROUP_ID')
        }
        
        return config 