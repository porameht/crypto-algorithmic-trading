import os
from dotenv import load_dotenv

def load_config():
    load_dotenv()

    config = {
        'api_main': os.getenv('API_BYBIT', None),
        'secret_main': os.getenv('SECRET_BYBIT', None),
        'accountType_main': os.getenv('ACCOUNT_TYPE', None),
        'api_worker1': os.getenv('API_BYBIT_WORKER1', None),
        'secret_worker1': os.getenv('SECRET_BYBIT_WORKER1', None),
        'accountType_worker1': os.getenv('ACCOUNT_TYPE_WORKER1', None),
        'title_api_main': 'combined_macd_cdc_signal',
        'title_api_worker1': 'combined_rsi_macd_ma_cdc_signal',
        'mode': 1,  # 1 - Isolated, 0 - Cross
        'leverage': 10,  # 10x
        'timeframe': 720,
        'timeframe_worker1': 5,  # 15 minutes
        'qty': 10,  # Amount of USDT for one order
        'max_positions': 7,  # Max 10 positions
        
        'telegram_bot_token': os.getenv('TELEGRAM_BOT_TOKEN', None),
        "telegram_user_id": os.getenv('TELEGRAM_USER_ID', None),
        'telegram_group_id': os.getenv('TELEGRAM_GROUP_ID', None)
    }

    return config
