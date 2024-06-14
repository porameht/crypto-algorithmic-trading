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
        'title_api_main': 'Main Account',
        'title_api_worker1': 'Worker 1',
        'mode': 1,  # 1 - Isolated, 0 - Cross
        'leverage': 10,  # 10x
        'timeframe': 5,
        'timeframe_worker1': 30,  # 15 minutes
        'qty': 10,  # Amount of USDT for one order
        'max_positions': 10,  # Max 10 positions
        'line_channel_access_token': os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None),
        "line_user_id": os.getenv('LINE_USER_ID', None)
    }

    return config
