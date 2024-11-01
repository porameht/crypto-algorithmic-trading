from src.utils.config_loader import ConfigLoader
from src.exchanges.bybit_exchange import BybitExchange
from src.notifications.telegram_notifier import TelegramNotifier
from src.strategies.rsi_strategy import RSIStrategy
from src.strategies.macd_strategy import MACDStrategy
from src.strategies.jim_simons_strategy import JimSimonsStrategy
from src.bots.trading_bot import TradingBot
from src.utils.logger import setup_logger
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = setup_logger(__name__)

def main():
    # Load configuration
    config = ConfigLoader.load_config()
    if not config:
        logger.error("Failed to load configuration")
        return
        
    # Initialize components
    exchange = BybitExchange(
        api_key=config['api_main'],
        api_secret=config['secret_main'],
        account_type=config['accountType_main']
    )
    
    notifier = TelegramNotifier(
        bot_token=config['telegram_bot_token'],
        group_id=config['telegram_group_id']
    )
    
    strategies = [
        JimSimonsStrategy(),
        RSIStrategy(),
        MACDStrategy()
    ]
    
    # Create bot instance
    bot = TradingBot(exchange, notifier, strategies, config)
    
    # Run bot with error handling
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(bot.run)
        try:
            future.result()
        except Exception as e:
            logger.error(f"Bot execution error: {e}")
            notifier.send_message(f"❌ Bot execution error: {e}")

if __name__ == "__main__":
    main()
