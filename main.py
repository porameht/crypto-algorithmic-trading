from config import load_config
from TradingBotBybit import TradingBotBybit

if __name__ == "__main__":
    config = load_config()

    if not all([config['api_main'], config['secret_main'], config['accountType_main']]):
        print("❌ Missing main account API credentials")
        exit(1)

    if not all([config['api_worker1'], config['secret_worker1'], config['accountType_worker1']]):
        print("❌ Missing worker1 account API credentials")
        exit(1)

    Bot = TradingBotBybit(config)
    Bot.run()
