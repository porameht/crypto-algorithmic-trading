from concurrent.futures import ThreadPoolExecutor, as_completed
from TelegramBot import TelegramBot
from config import load_config
from TradingBotBybit import TradingBotBybit
from AccountInfoDisplayer import AccountInfoDisplayer
from indicators.comb_rsi_macd_signal import comb_rsi_macd_signal
from indicators.rsi_basic_signal import rsi_basic_signal
from indicators.jim_simons import jim_simons_signal
from indicators.macd_signal import macd_signal
from indicators.comb_rsi_cdc_signal import comb_rsi_cdc_signal
from datetime import datetime, timedelta
import logging
import pytz
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def display_and_notify_account_info(index, bot, telegram, session_config):
    try:
        account_displayer = AccountInfoDisplayer(
            session=bot.session,
            title=f"No.{index+1}",
            timeframe=bot.timeframe,
            telegram=telegram,
            func_name=", ".join(f.__name__ for f in session_config['signal_funcs']),
            enable_logging=False
        )
        account_displayer.display_account_info()
    except Exception as e:
        logger.error(f"Error displaying account info: {e}", exc_info=True)
        telegram.send_message(f"❌ Error getting account info: {str(e)}")
        
def main():
    logger.info("Starting trading bot...")
    
    config = load_config()
    if not config:
        logger.error("Failed to load configuration")
        return
        
    telegram = TelegramBot(config)
    telegram.send_message("🤖 Bot is running...")
    
    # Define all available signal functions
    signal_functions = {
        'comb_rsi_macd': comb_rsi_macd_signal,
        'rsi_basic': rsi_basic_signal,
        'macd': macd_signal,
        'jim_simons': jim_simons_signal,
        'comb_rsi_cdc': comb_rsi_cdc_signal,
    }

    session_configs = [
        {
            'api': config.get('api_main'),
            'secret': config.get('secret_main'), 
            'accountType': config.get('accountType_main'),
            'mode': config.get('mode'),
            'leverage': config.get('leverage'),
            'timeframe': config.get('timeframe'),
            'qty': config.get('qty'),
            'max_positions': config.get('max_positions'),
            'signal_funcs': [
                signal_functions['jim_simons'],  # Start with simpler signals
                signal_functions['rsi_basic'],
                signal_functions['macd'],
                signal_functions['comb_rsi_cdc'],
                signal_functions['comb_rsi_macd'],
            ],
            'interval': config.get('account_info_telegram_time'),
            'telegram_bot_token': config.get('telegram_bot_token'),
            'telegram_group_id': config.get('telegram_group_id')
        }
    ]

    # Create bot instances
    bots = []
    
    for index, session_config in enumerate(session_configs):
        # Validate required config values
        required_fields = ['api', 'secret', 'accountType', 'mode', 'leverage', 'timeframe', 'qty', 'max_positions']
        if not all(field in session_config and session_config[field] for field in required_fields):
            missing_fields = [f for f in required_fields if f not in session_config or not session_config[f]]
            error_msg = f"❌ Missing required configuration fields: {missing_fields}"
            logger.error(error_msg)
            telegram.send_message(error_msg)
            continue
        
        try:
            bot = TradingBotBybit(session_config)
            bots.append(bot)
            display_and_notify_account_info(index, bot, telegram, session_config)
            logger.info(f"Successfully initialized bot with timeframe {bot.timeframe}")
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}", exc_info=True)
            telegram.send_message(f"❌ Failed to initialize bot: {str(e)}")

    if not bots:
        logger.error("No bots were successfully initialized")
        telegram.send_message("❌ No bots were successfully initialized")
        return

    # Run bots concurrently with error handling
    with ThreadPoolExecutor(max_workers=len(bots)) as executor:
        futures = []
        
        for bot in bots:
            def run_bot_with_notifications(bot=bot):
                while True:
                    try:
                        bangkok_tz = pytz.timezone('Asia/Bangkok')
                        current_time = datetime.now(bangkok_tz)
                        current_hour = current_time.hour
                        current_minute = current_time.minute
                        
                        # Check if it's one of the target hours (every 3 hours: 0, 3, 6, 9, 12, 15, 18, 21)
                        if current_hour % int(session_config.get('interval')) == 0 and current_minute == 0:
                            logger.info(f"Sending periodic account info update for {bot.timeframe}")
                            index = bots.index(bot)
                            display_and_notify_account_info(index, bot, telegram, session_configs[index])
                        bot.run()
                    except Exception as err:
                        error_msg = f"❌ Error in bot execution: {str(err)}"
                        logger.error(error_msg, exc_info=True)
                        telegram.send_message(error_msg)
            
            futures.append(executor.submit(run_bot_with_notifications))
        
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as err:
                error_msg = f"❌ Error in bot execution: {str(err)}"
                logger.error(error_msg, exc_info=True)
                telegram.send_message(error_msg)

if __name__ == "__main__":
    main()
