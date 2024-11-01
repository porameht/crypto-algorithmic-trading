from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pytz
from time import sleep
from pybit.unified_trading import HTTP
from ..core.interfaces.exchange_interface import ExchangeInterface

class BybitExchange(ExchangeInterface):
    def __init__(self, api_key: str, api_secret: str, account_type: str):
        self.session = HTTP(api_key=api_key, api_secret=api_secret)
        self.account_type = account_type
        
    def get_balance(self) -> float:
        try:
            resp = self.session.get_wallet_balance(
                accountType=self.account_type, 
                coin="USDT"
            )['result']['list'][0]['coin'][0]['walletBalance']
            return round(float(resp), 3)
        except Exception as e:
            print(f"Error getting balance: {e}")
            return 0.0

    def get_positions(self, limit: int = 200) -> List[Dict]:
        try:
            resp = self.session.get_positions(
                category='linear',
                settleCoin='USDT',
                limit=limit
            )['result']['list']
            
            positions = []
            for pos in resp:
                if float(pos['size']) > 0:  # Only include active positions
                    positions.append({
                        'symbol': pos['symbol'],
                        'avgPrice': float(pos['avgPrice']),
                        'side': pos['side'],
                        'size': float(pos['size']),
                        'takeProfit': float(pos['takeProfit']) if pos['takeProfit'] else None,
                        'stopLoss': float(pos['stopLoss']) if pos['stopLoss'] else None
                    })
            return positions
        except Exception as e:
            print(f"Error getting positions: {e}")
            return []

    def get_symbols(self) -> List[str]:
        try:
            resp = self.session.get_tickers(category='linear')
            return [ticker['symbol'] for ticker in resp['result']['list'] 
                   if ticker['symbol'].endswith('USDT')]
        except Exception as e:
            print(f"Error getting symbols: {e}")
            return []

    def get_last_price(self, symbol: str) -> float:
        try:
            resp = self.session.get_tickers(
                category='linear',
                symbol=symbol
            )['result']['list'][0]['lastPrice']
            return float(resp)
        except Exception as e:
            print(f"Error getting last price for {symbol}: {e}")
            return 0.0

    def place_order_market(self, 
                          symbol: str, 
                          side: str, 
                          mode: str, 
                          leverage: int, 
                          qty: float, 
                          take_profit: float, 
                          stop_loss: float) -> bool:
        try:
            # Set trading mode and leverage
            self._set_mode(symbol, mode)
            sleep(0.5)
            self._set_leverage(symbol, leverage)
            sleep(0.5)
            
            # Get price and quantity precisions
            price_precision, qty_precision = self._get_precisions(symbol)
            
            # Calculate order quantity
            mark_price = self.get_last_price(symbol)
            order_qty = round(qty / mark_price, qty_precision)
            
            # Place the order
            resp = self.session.place_order(
                category='linear',
                symbol=symbol,
                side=side,
                orderType='Market',
                qty=order_qty,
                takeProfit=round(take_profit, price_precision),
                stopLoss=round(stop_loss, price_precision),
                tpTriggerBy='LastPrice',
                slTriggerBy='LastPrice'
            )
            
            return resp['retCode'] == 0
            
        except Exception as e:
            print(f"Error placing order for {symbol}: {e}")
            return False

    def get_last_order_time(self, last_hours: int = 1) -> Dict[str, datetime]:
        try:
            end_time = datetime.now(pytz.UTC)
            start_time = end_time - timedelta(hours=last_hours)
            
            orders = self.session.get_orders(
                category='linear',
                startTime=int(start_time.timestamp() * 1000),
                endTime=int(end_time.timestamp() * 1000)
            )['result']['list']
            
            return {
                order['symbol']: datetime.fromtimestamp(
                    int(order['createdTime']) / 1000, 
                    pytz.UTC
                )
                for order in orders
            }
            
        except Exception as e:
            print(f"Error getting last order times: {e}")
            return {}

    def get_net_profit(self, last_hours: int = 12) -> float:
        try:
            end_time = datetime.now(pytz.UTC)
            start_time = end_time - timedelta(hours=last_hours)
            
            closed_pnl = self.session.get_closed_pnl(
                category='linear',
                startTime=int(start_time.timestamp() * 1000),
                endTime=int(end_time.timestamp() * 1000)
            )['result']['list']
            
            return sum(float(pnl['closedPnl']) for pnl in closed_pnl)
            
        except Exception as e:
            print(f"Error getting net profit: {e}")
            return 0.0

    def _set_mode(self, symbol: str, mode: str) -> None:
        try:
            self.session.switch_margin_mode(
                category='linear',
                symbol=symbol,
                tradeMode=1 if mode == 'ISOLATED' else 0
            )
        except Exception as e:
            if 'margin mode is not modified' not in str(e).lower():
                print(f"Error setting mode for {symbol}: {e}")

    def _set_leverage(self, symbol: str, leverage: int) -> None:
        try:
            self.session.set_leverage(
                category='linear',
                symbol=symbol,
                buyLeverage=str(leverage),
                sellLeverage=str(leverage)
            )
        except Exception as e:
            if 'leverage not modified' not in str(e).lower():
                print(f"Error setting leverage for {symbol}: {e}")

    def _get_precisions(self, symbol: str) -> tuple[int, int]:
        try:
            instruments = self.session.get_instruments_info(
                category='linear',
                symbol=symbol
            )['result']['list'][0]
            
            return (
                int(instruments['priceScale']),
                int(instruments['lotSizeScale'])
            )
        except Exception as e:
            print(f"Error getting precisions for {symbol}: {e}")
            return (8, 8)  # Default precisions 