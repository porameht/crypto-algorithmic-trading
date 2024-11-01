from concurrent.futures import ThreadPoolExecutor, as_completed
from TelegramBot import TelegramBot
from config import load_config
from TradingBotBybit import TradingBotBybit
from indicators.comb_rsi_macd_signal import comb_rsi_macd_signal
from indicators.rsi_basic_signal import rsi_basic_signal
from indicators.jim_simons import jim_simons_signal
from indicators.comb_rsi_cdc_signal import comb_rsi_cdc_signal
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def get_signal_functions():
    """
    Define and return available signal functions.
    
    Returns:
        dict: Mapping of signal function names to their implementations
    """
    signal_functions = {
        'comb_rsi_macd': comb_rsi_macd_signal,
        'rsi_basic': rsi_basic_signal, 
        'jim_simons': jim_simons_signal,
        'comb_rsi_cdc': comb_rsi_cdc_signal,
    }
    return signal_functions

def create_session_config(config, signal_functions):
    """
    Create session configuration from config and signal functions.
    
    Args:
        config (dict): Raw configuration dictionary
        signal_functions (dict): Available signal functions
        
    Returns:
        dict: Complete session configuration
    """
    # API credentials
    credentials = {
        'api': config.get('api_main'),
        'secret': config.get('secret_main'),
        'accountType': config.get('accountType_main'),
    }
    
    # Trading parameters
    trading_params = {
        'mode': config.get('mode'),
        'leverage': config.get('leverage'), 
        'timeframe': config.get('timeframe'),
        'qty': config.get('qty'),
        'max_positions': config.get('max_positions'),
    }
    
    # Signal function configuration
    signal_funcs = [
        signal_functions['jim_simons'],
        signal_functions['rsi_basic'],
        signal_functions['comb_rsi_cdc'], 
        signal_functions['comb_rsi_macd'],
    ]
    
    # Telegram settings
    telegram_config = {
        'interval': config.get('account_info_telegram_time'),
        'telegram_bot_token': config.get('telegram_bot_token'),
        'telegram_group_id': config.get('telegram_group_id')
    }
    
    # Combine all configurations
    session_config = {
        **credentials,
        **trading_params,
        'signal_funcs': signal_funcs,
        **telegram_config
    }
    
    return session_config

def validate_session_config(session_config, telegram):
    """Validate required fields in session config"""
    required_fields = ['api', 'secret', 'accountType', 'mode', 'leverage', 'timeframe', 'qty', 'max_positions']
    
    if not all(field in session_config and session_config[field] for field in required_fields):
        missing_fields = [f for f in required_fields if f not in session_config or not session_config[f]]
        error_msg = f"❌ Missing required configuration fields: {missing_fields}"
        logger.error(error_msg)
        telegram.send_message(error_msg)
        return False
    return True

def initialize_bot(session_config, telegram):
    """Initialize a trading bot instance"""
    try:
        bot = TradingBotBybit(session_config)
        logger.info(f"Successfully initialized bot with timeframe {bot.timeframe}")
        return bot
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}", exc_info=True)
        telegram.send_message(f"❌ Failed to initialize bot: {str(e)}")
        return None

def run_bots(bots, telegram):
    """Run multiple bots concurrently with error handling"""
    with ThreadPoolExecutor(max_workers=len(bots)) as executor:
        futures = []
        
        for bot in bots:
            futures.append(executor.submit(bot.run))
        
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as err:
                error_msg = f"❌ Error in bot execution: {str(err)}"
                logger.error(error_msg, exc_info=True)
                telegram.send_message(error_msg)

def main():
    logger.info("Starting trading bot...")
    
    config = load_config()
    if not config:
        logger.error("Failed to load configuration")
        return
        
    telegram = TelegramBot(config)
    telegram.send_message("🤖 Bot is running...")
    
    signal_functions = get_signal_functions()
    session_configs = [create_session_config(config, signal_functions)]
    
    # Create bot instances
    bots = []
    
    for session_config in session_configs:
        if validate_session_config(session_config, telegram):
            bot = initialize_bot(session_config, telegram)
            if bot:
                bots.append(bot)

    if not bots:
        logger.error("No bots were successfully initialized")
        telegram.send_message("❌ No bots were successfully initialized")
        return

    run_bots(bots, telegram)

if __name__ == "__main__":
    main()
