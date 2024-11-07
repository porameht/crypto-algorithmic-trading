from time import sleep
from rich import print
from Bybit import Bybit
from datetime import datetime
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@dataclass
class ArbitrageOpportunity:
    base_symbol: str
    quote_symbol1: str 
    quote_symbol2: str
    profit_percentage: float
    required_base_amount: float
    estimated_profit: float
    path: List[Tuple[str, str, float]]

class TriangularArbitrageWorker:
    def __init__(self, session_config: dict) -> None:
        """Initialize TriangularArbitrageWorker with configuration settings."""
        logger.info("Initializing TriangularArbitrageWorker...")
        self.min_profit_threshold = session_config.get('min_profit_threshold', 0.5)  # 0.1%
        self.trade_amount = session_config.get('trade_amount', 5)  # Base amount in USDT
        self.base_currency = session_config.get('base_currency', 'USDT')
        self.execution_delay = session_config.get('execution_delay', 20)  # Delay between checks in seconds
        logger.info(f"Worker initialized with: min_profit={self.min_profit_threshold}%, trade_amount={self.trade_amount} {self.base_currency}")
        self._init_session(session_config)

    def _init_session(self, session_config: dict) -> None:
        """Initialize Bybit trading session."""
        logger.info("Initializing Bybit session...")
        self.session = Bybit(
            session_config['api'], 
            session_config['secret'],
            session_config['accountType']
        )
        self.symbols = []
        
        # Get all available trading pairs
        symbol_info = self.session.get_ticket_by_symbol()
        
        # Find triangular arbitrage opportunities
        # Example: BTC/ETH -> ETH/LTC -> LTC/BTC
        triangular_pairs = []
        for symbol1 in symbol_info:
            base1, quote1 = symbol1[:3], symbol1[3:] # Split first pair
            
            # Find second pair starting with quote1
            for symbol2 in symbol_info:
                if symbol2.startswith(quote1):
                    quote2 = symbol2[3:] # Get quote of second pair
                    
                    # Find third pair to complete the triangle
                    target_symbol = f"{quote2}{base1}"
                    if target_symbol in symbol_info:
                        triangular_pairs.append([symbol1, symbol2, target_symbol])
                        
        logger.info(f"Found {len(triangular_pairs)} potential triangular paths")
        print(f"Example path: {triangular_pairs[0] if triangular_pairs else 'None found'}")
        # for symbol in major_coins:
        #     try:
        #         symbol_info = self.session.get_ticket_by_symbol(symbol)
        #         if symbol_info and len(symbol_info) > 0:
        #             self.symbols.append({
        #                 'symbol': symbol_info[0]['symbol'],
        #                 'lastPrice': float(symbol_info[0]['lastPrice']),
        #                 'bidPrice': float(symbol_info[0]['bid1Price']),
        #                 'askPrice': float(symbol_info[0]['ask1Price']),
        #                 'bidSize': float(symbol_info[0]['bid1Size']),
        #                 'askSize': float(symbol_info[0]['ask1Size'])
        #             })
        #             logger.info(f"Added trading pair: {symbol}")
        #     except Exception as e:
        #         logger.error(f"Error adding symbol {symbol}: {str(e)}")
        # self.session_config = session_config
        # logger.info(f"Session initialized with {len(self.symbols)} trading pairs")

    def get_trading_pairs(self) -> Dict[str, Dict[str, float]]:
        """Get all trading pairs and their current prices."""
        print("Fetching current trading pair prices...")
        pairs = {}
        for symbol_data in self.symbols:
            symbol = symbol_data['symbol']
            print(f"Fetching price for {symbol}")
            try:
                pairs[symbol] = {
                    'lastPrice': symbol_data['lastPrice'],
                    'bidPrice': symbol_data['bidPrice'],
                    'askPrice': symbol_data['askPrice'],
                    'bidSize': symbol_data['bidSize'],
                    'askSize': symbol_data['askSize']
                }
            except Exception as e:
                logger.error(f"Error getting price for {symbol}: {e}")
        print(f"Retrieved prices for {len(pairs)} trading pairs")
        return pairs

    def find_triangular_opportunities(self) -> List[ArbitrageOpportunity]:
        """Find all possible triangular arbitrage opportunities."""
        print("Searching for triangular arbitrage opportunities...")
        opportunities = []
        pairs = self.get_trading_pairs()
        
        # Find all possible triangular combinations
        for symbol1 in pairs:
            for symbol2 in pairs:
                for symbol3 in pairs:
                    print(f"Checking {symbol1}->{symbol2}->{symbol3}")
                    opportunity = self._check_triangular_arbitrage(
                        symbol1, symbol2, symbol3, pairs
                    )
                    if opportunity:
                        opportunities.append(opportunity)
        
        logger.info(f"Found {len(opportunities)} potential arbitrage opportunities")
        return opportunities

    def _check_triangular_arbitrage(
        self,
        symbol1: str,
        symbol2: str,
        symbol3: str,
        pairs: Dict[str, Dict[str, float]]
    ) -> Optional[ArbitrageOpportunity]:
        """Check if there's an arbitrage opportunity in the given triangle."""
        try:
            # Example from image: BTC -> ETH -> LTC -> BTC
            # Trade 1: BTC to ETH (ETH/BTC)
            # Trade 2: ETH to LTC (ETH/LTC)
            # Trade 3: LTC to BTC (BTC/LTC)
            
            pair1 = pairs.get(symbol1)  # ETH/BTC rate
            pair2 = pairs.get(symbol2)  # ETH/LTC rate
            pair3 = pairs.get(symbol3)  # BTC/LTC rate

            if not all([pair1, pair2, pair3]):
                return None

            # Calculate the complete cycle
            # Starting with 1 BTC:
            # 1. BTC -> ETH: multiply by ETH/BTC rate
            step1_amount = 1 * pair1['bidPrice']  # Get ETH
            
            # 2. ETH -> LTC: multiply by ETH/LTC rate
            step2_amount = step1_amount * pair2['bidPrice']  # Get LTC
            
            # 3. LTC -> BTC: multiply by BTC/LTC rate
            final_btc_amount = step2_amount * pair3['bidPrice']  # Get BTC back

            # Calculate profit percentage
            profit_percentage = ((final_btc_amount / 1) - 1) * 100
            
            print(f"🟢 Profit percentage: {profit_percentage}%")

            # Add sanity check for unrealistic profits
            if profit_percentage > 5:  # Cap at 5% profit to filter out anomalies
                return None

            # Consider available liquidity
            min_size = min(
                pair1['bidSize'],
                pair2['bidSize'],
                pair3['bidSize']
            )

            if profit_percentage > self.min_profit_threshold and min_size >= self.trade_amount:
                estimated_profit = self.trade_amount * (profit_percentage / 100)
                logger.debug(f"Found opportunity: {symbol1}->{symbol2}->{symbol3} with {profit_percentage:.2f}% profit")
                return ArbitrageOpportunity(
                    base_symbol=symbol1.split('/')[0],  # BTC
                    quote_symbol1=symbol2.split('/')[0],  # ETH
                    quote_symbol2=symbol3.split('/')[0],  # LTC
                    profit_percentage=profit_percentage,
                    required_base_amount=self.trade_amount,
                    estimated_profit=estimated_profit,
                    path=[(symbol1, "trade", pair1['bidPrice']), 
                          (symbol2, "trade", pair2['bidPrice']), 
                          (symbol3, "trade", pair3['bidPrice'])]
                )

        except Exception as e:
            logger.error(f"Error checking arbitrage opportunity: {e}")
        
        return None

    def run(self) -> None:
        """Main execution loop."""
        logger.info("Starting triangular arbitrage worker...")
        while True:
            if not self._check_connection():
                continue
                
            print('🤖 Triangular Arbitrage Worker started')
            print("Starting new arbitrage scan cycle")
            opportunities = self.find_triangular_opportunities()
            
            for opportunity in opportunities:
                if opportunity.profit_percentage > self.min_profit_threshold:
                    logger.info(f"Found opportunity: {opportunity}")
                    self.session.execute_arbitrage(opportunity, self.trade_amount)

            logger.debug(f"Sleeping for {self.execution_delay} seconds")
            sleep(self.execution_delay)
                
    def _check_connection(self) -> bool:
        """Check if connection to Bybit is active."""
        logger.debug("Checking Bybit connection...")
        balance = self.session.get_balance()
        
        if balance is None or self.symbols is None:
            logger.error('Cannot connect to Bybit')
            print('❌ Cannot connect to Bybit')
            sleep(120)
            return False
        logger.debug("Connection to Bybit OK")
        return True 