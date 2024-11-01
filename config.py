import os
from dotenv import load_dotenv

def load_config():
    load_dotenv()

    config = {
        'api_main': os.getenv('API_BYBIT', None),
        'secret_main': os.getenv('SECRET_BYBIT', None),
        'accountType_main': os.getenv('ACCOUNT_TYPE', None),
        'account_info_telegram_time': os.getenv('ACCOUNT_INFO_TELEGRAM_TIME', None),
        'timeframe': os.getenv('TIMEFRAME', 30),

        # 'api_worker1': os.getenv('API_BYBIT_WORKER1', None),
        # 'secret_worker1': os.getenv('SECRET_BYBIT_WORKER1', None),
        # 'accountType_worker1': os.getenv('ACCOUNT_TYPE_WORKER1', None),
        # 'timeframe_worker1': os.getenv('TIMEFRAME_WORKER1', 30),  # 15 minutes

        'mode': os.getenv('MODE', 1),  # 1 - Isolated, 0 - Cross
        'leverage': os.getenv('LEVERAGE', 10),  # 10x
        'qty': os.getenv('QTY', 10),  # Amount of USDT for one order
        'max_positions': os.getenv('MAX_POSITIONS', 10),  # Max 10 positions
        
        'telegram_bot_token': os.getenv('TELEGRAM_BOT_TOKEN', None),
        'telegram_group_id': os.getenv('TELEGRAM_GROUP_ID', None)
    }

    return config
