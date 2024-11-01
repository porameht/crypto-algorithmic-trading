from typing import List, Dict
from datetime import datetime
import pytz
from time import sleep

from ..core.interfaces.bot_interface import BotInterface
from ..core.interfaces.exchange_interface import ExchangeInterface
from ..core.interfaces.notification_interface import NotificationInterface
from ..core.interfaces.strategy_interface import StrategyInterface
from ..utils.account_info_displayer import AccountInfoDisplayer
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class BaseBot(BotInterface):
    def __init__(self,
                 exchange: ExchangeInterface,
                 notifier: NotificationInterface,
                 strategies: List[StrategyInterface],
                 config: Dict):
        self.exchange = exchange
        self.notifier = notifier
        self.strategies = strategies
        self.config = config
        self.timeframe = config['timeframe']
        self.mode = config['mode']
        self.leverage = config['leverage']
        self.qty = config['qty']
        self.max_positions = config['max_positions']
        self.account_info_interval = int(config.get('account_info_telegram_time', 3))
        
        self.account_displayer = AccountInfoDisplayer(
            exchange=exchange,
            notifier=notifier,
            strategy_names=[s.__class__.__name__ for s in strategies],
            timeframe=self.timeframe
        )
    
    def run(self) -> None:
        """Main bot execution loop"""
        try:
            while True:
                try:
                    positions = [p['symbol'] for p in self.exchange.get_positions()]
                    self.execute_trades(positions)
                    
                    # Check if it's time to display account info
                    bangkok_tz = pytz.timezone('Asia/Bangkok')
                    current_time = datetime.now(bangkok_tz)
                    if (current_time.hour % self.account_info_interval == 0 and 
                        current_time.minute == 0):
                        self.display_account_info()
                        
                    sleep(60)  # Wait for 1 minute before next iteration
                    
                except Exception as e:
                    error_msg = f"Error in bot execution loop: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    self.notifier.send_message(f"❌ {error_msg}")
                    sleep(60)  # Wait before retrying
                    
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            self.notifier.send_message("🛑 Bot stopped by user")
    
    def execute_trades(self, positions: List[str]) -> None:
        """Execute trading logic - to be implemented by specific bots"""
        raise NotImplementedError
        
    def display_account_info(self) -> None:
        """Display account information"""
        try:
            self.account_displayer.display_account_info()
        except Exception as e:
            error_msg = f"Error displaying account info: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.notifier.send_message(f"❌ {error_msg}") 