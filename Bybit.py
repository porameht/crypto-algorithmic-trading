from datetime import datetime, timedelta
from pybit.unified_trading import HTTP
import pandas as pd
import ta
from time import sleep

class Bybit:
    def __init__(self, api, secret, accounttype):
        self.api = api
        self.secret = secret
        self.accountType = accounttype
        self.session = HTTP(api_key=self.api, api_secret=self.secret)

    def get_balance(self):
        try:
            resp = self.session.get_wallet_balance(accountType=self.accountType, coin="USDT")['result']['list'][0]['coin'][0]['walletBalance']
            resp = round(float(resp), 3)
            return resp
        except Exception as err:
            print(err)

    def get_positions(self, limit=20):
        try:
            resp = self.session.get_positions(
                category='linear',
                settleCoin='USDT',
                limit=limit
            )['result']['list']
            pos = []
            for elem in resp:
                pos.append({
                    'symbol': elem['symbol'],
                    'avgPrice': elem['avgPrice'],
                    'side': elem['side'],
                    'size': elem['size'],
                    'takeProfit': elem['takeProfit'],
                    'stopLoss': elem['stopLoss']
                })
            return pos
        except Exception as err:
            print(err)

    def get_last_pnl(self, limit=50):
        try:
            resp = self.session.get_closed_pnl(category="linear", limit=limit)['result']['list']
            pnl = 0
            for elem in resp:
                pnl += float(elem['closedPnl'])
            return round(pnl, 4)
        except Exception as err:
            print(err)
            
    def get_net_profit(self, last_hours):
        net_profit = 0.0  # Initialize net profit
        try:
            start_time = int((datetime.now() - timedelta(hours=last_hours)).timestamp() * 1000)
            end_time = int(datetime.now().timestamp() * 1000)
            order_history = self.session.get_closed_pnl(category="linear", limit=100, start_time=start_time, end_time=end_time)['result']['list']
            for order in order_history:
                closed_pnl = float(order['closedPnl'])
                updated_time = int(order['updatedTime'])  # Convert string to integer
                updated_datetime = datetime.fromtimestamp(updated_time / 1000)
                if updated_datetime >= datetime.now() - timedelta(hours=last_hours):
                    net_profit += closed_pnl  # Sum the closed PnL

            return net_profit 
        except Exception as err:
            print(f"Error fetching order history: {err}")
            return net_profit  # Return net profit even if there's an error

    def get_current_pnl(self):
        try:
            resp = self.session.get_positions(
                category="linear",
                settleCoin="USDT"
            )['result']['list']
            pnl = 0
            for elem in resp:
                pnl += float(elem['unrealisedPnl'])
            return round(pnl, 4)
        except Exception as err:
            print(err)

    def get_tickers(self):
        try:
            resp = self.session.get_tickers(category="linear")['result']['list']
            symbols = []
            for elem in resp:
                if 'USDT' in elem['symbol'] and not 'USDC' in elem['symbol']:
                    symbols.append(elem['symbol'])
            return symbols
        except Exception as err:
            print(err)
            
    def get_ticket_by_symbol(self):
        try:
            resp = self.session.get_tickers(category="spot")['result']['list']
            symbols = []
            for item in resp:
                symbols.append(item['symbol'])
            # if symbol in ['ETHBTC', 'LTCETH', 'LTCBTC']:
            #     return resp
            return symbols
        except Exception as err:
            print(err)
    def get_last_order_time(self, last_hours=1):
        last_order_times = {}
        try:
            start_time = int((datetime.now() - timedelta(hours=last_hours)).timestamp() * 1000)
            end_time = int(datetime.now().timestamp() * 1000)
            order_history = self.session.get_closed_pnl(category="linear", limit=100, start_time=start_time, end_time=end_time)['result']['list']
            for order in order_history:
                
                closed_pnl = float(order['closedPnl'])
                # if closed_pnl < 0:
                #     continue
                
                symbol = order['symbol']
                updated_time = int(order['updatedTime'])  # Convert string to integer
                updated_datetime = datetime.fromtimestamp(updated_time / 1000)
                if updated_datetime >= datetime.now() - timedelta(hours=last_hours):
                    last_order_times[symbol] = updated_datetime, closed_pnl
                    
            return last_order_times
        except Exception as err:
            print(f"Error fetching order history: {err}")
        return last_order_times

    def klines(self, symbol, timeframe, limit=500):
        try:
            resp = self.session.get_kline(
                category='linear',
                symbol=symbol,
                interval=timeframe,
                limit=limit
            )['result']['list']
            
            resp = pd.DataFrame(resp)
            resp.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Turnover']
            resp = resp.set_index('Time')
            resp = resp.astype(float)
            resp = resp[::-1]
            
            return resp
        except Exception as err:
            print(err)

    def get_precisions(self, symbol):
        try:
            resp = self.session.get_instruments_info(
                category='linear',
                symbol=symbol
            )['result']['list'][0]
            price = resp['priceFilter']['tickSize']
            if '.' in price:
                price = len(price.split('.')[1])
            else:
                price = 0
            qty = resp['lotSizeFilter']['qtyStep']
            if '.' in qty:
                qty = len(qty.split('.')[1])
            else:
                qty = 0
            return price, qty
        except Exception as err:
            print(err)

    def get_max_leverage(self, symbol):
        try:
            resp = self.session.get_instruments_info(
                category="linear",
                symbol=symbol,
            )['result']['list'][0]['leverageFilter']['maxLeverage']
            return float(resp)
        except Exception as err:
            print(err)

    def set_mode(self, symbol, mode=1, leverage=10):
        try:
            resp = self.session.switch_margin_mode(
                category='linear',
                symbol=symbol,
                tradeMode=str(mode),
                buyLeverage=str(leverage),
                sellLeverage=str(leverage)
            )
            if resp['retMsg'] == 'OK':
                if mode == 1:
                    print(f'[{symbol}] Changed margin mode to ISOLATED')
                if mode == 0:
                    print(f'[{symbol}] Changed margin mode to CROSS')
        except Exception as err:
            if '110026' in str(err):
                print(f'[{symbol}] Margin mode is Not changed')
            else:
                print(err)

    def set_leverage(self, symbol, leverage=10):
        try:
            resp = self.session.set_leverage(
                category="linear",
                symbol=symbol,
                buyLeverage=str(leverage),
                sellLeverage=str(leverage),
            )
            if resp['retMsg'] == 'OK':
                print(f'[{symbol}] Changed leverage to {leverage}')
        except Exception as err:
            if '110043' in str(err):
                print(f'[{symbol}] Leverage is Not changed')
            else:
                print(err)

    # def place_order_market(self, symbol, side, mode, leverage, qty=10, tp=0.012, sl=0.009):
    #     # Set trading mode and leverage
    #     self.set_mode(symbol, mode, leverage)
    #     sleep(0.5)
    #     self.set_leverage(symbol, leverage)
    #     sleep(0.5)
        
    #     # Get price and quantity precisions
    #     price_precision = self.get_precisions(symbol)[0]
    #     qty_precision = self.get_precisions(symbol)[1]
        
    #     # Get the current mark price
    #     mark_price = self.session.get_tickers(
    #         category='linear',
    #         symbol=symbol
    #     )['result']['list'][0]['markPrice']
    #     mark_price = float(mark_price)
    #     # Calculate order quantity based on mark price
    #     order_qty = round(qty / mark_price, qty_precision)
    #     sleep(2)

    #     try:
    #         if side.lower() == 'buy':
    #             tp_price = round(tp, price_precision)
    #             sl_price = round(sl, price_precision)
    #             resp = self.session.place_order(
    #                 category='linear',
    #                 symbol=symbol,
    #                 side='Buy',
    #                 orderType='Market',
    #                 qty=order_qty,
    #                 takeProfit=tp_price,
    #                 stopLoss=sl_price,
    #             )
    #             print(f'Takeprofit: {tp_price}')
    #             print(f'Stoploss: {sl_price}')
    #             print(resp['retMsg'])
    #             return resp['retMsg']

    #         elif side.lower() == 'sell':
    #             tp_price = round(tp, price_precision)
    #             sl_price = round(sl, price_precision)
    #             resp = self.session.place_order(
    #                 category='linear',
    #                 symbol=symbol,
    #                 side='Sell',
    #                 orderType='Market',
    #                 qty=order_qty,
    #                 takeProfit=tp_price,
    #                 stopLoss=sl_price,
    #             )
    #             print(f'Takeprofit: {tp_price}')
    #             print(f'Stoploss: {sl_price}')
    #             print(resp['retMsg'])
    #             return resp['retMsg']
    #         else:
    #             print("Invalid side specified. Use 'buy' or 'sell'.")

    #     except Exception as err:
    #         print(err)

    def place_order_limit(self, symbol, side, mode, leverage, qty=10, tp=0.012, sl=0.009):
        self.set_mode(symbol, mode, leverage)
        sleep(0.5)
        self.set_leverage(symbol, leverage)
        sleep(0.5)
        price_precision = self.get_precisions(symbol)[0]
        qty_precision = self.get_precisions(symbol)[1]
        limit_price = self.session.get_tickers(
            category='linear',
            symbol=symbol
        )['result']['list'][0]['lastPrice']
        limit_price = float(limit_price)
        order_qty = round(qty / limit_price, qty_precision)
        sleep(2)
        if side == 'buy':
            try:
                tp_price = round(limit_price + limit_price * tp, price_precision)
                sl_price = round(limit_price - limit_price * sl, price_precision)
                resp = self.session.place_order(
                    category='linear',
                    symbol=symbol,
                    side='Buy',
                    orderType='Limit',
                    price= limit_price,
                    qty=order_qty,
                    takeProfit=tp_price,
                    stopLoss=sl_price,
                    tpTriggerBy='LastPrice',
                    slTriggerBy='LastPrice'
                )
                print(resp['retMsg'])
            except Exception as err:
                print(err)

        if side == 'sell':
            try:
                tp_price = round(limit_price - limit_price * tp, price_precision)
                sl_price = round(limit_price + limit_price * sl, price_precision)
                resp = self.session.place_order(
                    category='linear',
                    symbol=symbol,
                    side='Sell',
                    orderType='Limit',
                    price=limit_price,
                    qty=order_qty,
                    takeProfit=tp_price,
                    stopLoss=sl_price,
                    tpTriggerBy='LastPrice',
                    slTriggerBy='LastPrice'
                )
                print(resp['retMsg'])
            except Exception as err:
                print(err)
                
    def get_win_rate(self):
        try:
            order_history = self.session.get_closed_pnl(category="linear", limit=100)['result']['list']
            wins = sum(1 for order in order_history if float(order['closedPnl']) > 0)
            total = len(order_history)
            return round((wins / total) * 100, 3) if total > 0 else 0.0
        except Exception as err:
            print(f"Error calculating win rate: {err}")
            return None
            
    
    def place_order_market(self, symbol, side, mode, leverage, qty, tp, sl=None, trailing_stop_percent=1):
        try:
            # Set trading mode and leverage
            self.set_mode(symbol, mode, leverage)
            sleep(0.5)
            self.set_leverage(symbol, leverage)
            sleep(0.5)
            
            # Get price and quantity precisions
            price_precision = self.get_precisions(symbol)[0]
            qty_precision = self.get_precisions(symbol)[1]
            
            # Get the current mark price
            mark_price_resp = self.session.get_tickers(
                category='linear',
                symbol=symbol
            )
            if 'result' not in mark_price_resp or 'list' not in mark_price_resp['result']:
                raise ValueError("Invalid response format when getting mark price")
                
            mark_price = float(mark_price_resp['result']['list'][0]['markPrice'])
            
            # Calculate order quantity based on mark price
            order_qty = round(qty / mark_price, qty_precision)
            
            sleep(2)

            # Place the market order
            order_resp = self.session.place_order(
                category='linear',
                symbol=symbol,
                side=side.capitalize(),
                orderType='Market',
                qty=str(order_qty),
                takeProfit=str(tp),
                stopLoss=str(sl) if sl else None,
            )
            
            if not order_resp or 'retMsg' not in order_resp:
                raise ValueError("Invalid order response format")
                
            print(f'🟢 Order placed: {order_resp["retMsg"]}')

            if order_resp['retMsg'] == 'OK':
                # Set TP, SL, and trailing stop
                stop_resp = self.set_trading_stop(side, symbol, mark_price, tp, sl, trailing_stop_percent)
                if not stop_resp:
                    raise ValueError("Failed to set trading stop")
                    
                print(f'🟢 Trading stop set: {stop_resp}')
                print(f'Side: {side.capitalize()}')
                print(f'Quantity: {order_qty}')
                print(f'Mark Price: {mark_price}')
                
                return True
            
            return False
        except Exception as err:
            print(f"❌ Error placing order: {err}")
            return False
    
    def set_trading_stop(self, side, symbol, mark_price, tp, sl, trailing_stop_percent):
        price_precision = self.get_precisions(symbol)[0]
        
        trailing_stop = round(mark_price * trailing_stop_percent/100, price_precision)
        
        try:
            resp = self.session.set_trading_stop(
                category='linear',
                symbol=symbol,
                takeProfit=str(tp),
                stopLoss=str(sl) if sl else None,
                trailingStop=str(trailing_stop),
                tpTriggerBy='MarkPrice',
                slTriggerBy='MarkPrice',
                tpslMode='Full',
                tpSize='',
                slSize=''
            )
            print(f'Take Profit: {tp}')
            print(f'Stop Loss: {sl}')
            print(f'Trailing Stop: {trailing_stop}')
            return resp['retMsg']
        except Exception as err:
            print(f"Error setting trading stop: {err}")
            return None

    def get_last_price(self, symbol):
        try:
            resp = self.session.get_tickers(
                category='linear',
                symbol=symbol
            )['result']['list'][0]['lastPrice']
            return float(resp)
        except Exception as err:
            print(err)
            return None

    def execute_arbitrage(self, opportunity, trade_amount):
        """Execute the triangular arbitrage trades.
        
        Args:
            opportunity: An object containing the arbitrage path and details
                       Expected format: {path: [(symbol, side, price), ...], profit_percentage: float}
                       
        Returns:
            bool: True if arbitrage executed successfully, False otherwise
        """
        try:            
            # Execute trades in sequence
            for symbol, side, price in opportunity.path:
                print(f"Placing {side} order for {symbol} at {price}")

                # Place spot market order
                result = self.session.place_order(
                    category="spot",
                    symbol=symbol,
                    side=side.capitalize(),
                    orderType="Market",
                    qty=str(trade_amount if side == "buy" else trade_amount * price),
                    isLeverage=0,  # Spot trading without margin
                    timeInForce="IOC"  # Immediate or cancel
                )
                
                if not result or result.get('retMsg') != 'OK':
                    print(f"❌ Failed to execute trade for {symbol}")
                    return False
                
                print(f"🟢 Successfully placed {side} order for {symbol}")
                sleep(1)  # Small delay between trades
            
            print(f"🟢 Successfully executed arbitrage with {opportunity.profit_percentage}% profit")
            return True

        except Exception as e:
            print(f"❌ Error executing arbitrage: {e}")
            return False
