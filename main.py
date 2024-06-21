from concurrent.futures import ThreadPoolExecutor, as_completed
from TelegramBot import TelegramBot
from config import load_config
from TradingBotBybit import TradingBotBybit
from indicators.combined_macd_cdc_signal import combined_macd_cdc_signal
from indicators.combined_rsi_cdc_signal import combined_rsi_cdc_signal
from indicators.combined_rsi_macd_signal import combined_rsi_macd_ma_cdc_signal
from indicators.rsi_basic_signal import rsi_basic_signal

    
def main():
    config = load_config()
    # telegram = TelegramBot(config)
    # telegram.send_message_group("🤖 Bot is running...")
    session_configs = [
        {
            'api': config['api_main'],
            'secret': config['secret_main'],
            'accountType': config['accountType_main'],
            'mode': config['mode'],
            'leverage': config['leverage'],
            'timeframe': config['timeframe'],
            'qty': config['qty'],
            'max_positions': config['max_positions'],
            'signal_func': combined_rsi_cdc_signal,
            'title': config['title_api_main']
        },
        {
            'api': config['api_worker1'],
            'secret': config['secret_worker1'],
            'accountType': config['accountType_worker1'],
            'mode': config['mode'],
            'leverage': config['leverage'],
            'timeframe': config['timeframe_worker1'],
            'qty': config['qty'],
            'max_positions': config['max_positions'],
            'signal_func': rsi_basic_signal,
            'title': config['title_api_worker1']
        }
    ]

    bots = [TradingBotBybit(session_config) for session_config in session_configs]

    with ThreadPoolExecutor(max_workers=len(bots)) as executor:
        futures = [executor.submit(bot.run) for bot in bots]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as err:
                print(f"Error in bot execution: {err}")

if __name__ == "__main__":
    main()
