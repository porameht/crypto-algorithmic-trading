from pybit.unified_trading import HTTP
import pandas as pd
import ta
from time import sleep
import random
import requests

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

    def place_order_market(self, symbol, side, mode, leverage, qty=10, tp=0.012, sl=0.009):
        # Set trading mode and leverage
        self.set_mode(symbol, mode, leverage)
        sleep(0.5)
        self.set_leverage(symbol, leverage)
        sleep(0.5)
        
        # Get price and quantity precisions
        price_precision = self.get_precisions(symbol)[0]
        qty_precision = self.get_precisions(symbol)[1]
        
        # Get the current mark price
        mark_price = self.session.get_tickers(
            category='linear',
            symbol=symbol
        )['result']['list'][0]['markPrice']
        mark_price = float(mark_price)
        # Calculate order quantity based on mark price
        order_qty = round(qty / mark_price, qty_precision)
        sleep(2)

        try:
            if side.lower() == 'buy':
                tp_price = round(tp, price_precision)
                sl_price = round(sl, price_precision)
                resp = self.session.place_order(
                    category='linear',
                    symbol=symbol,
                    side='Buy',
                    orderType='Market',
                    qty=order_qty,
                    takeProfit=tp_price,
                    stopLoss=sl_price,
                    # tpTriggerBy='Market',
                    # slTriggerBy='Market'
                )
                print(f'Takeprofit: {tp_price}')
                print(f'Stoploss: {sl_price}')
                print(resp['retMsg'])
                return resp['retMsg']

            elif side.lower() == 'sell':
                tp_price = round(tp, price_precision)
                sl_price = round(sl, price_precision)
                resp = self.session.place_order(
                    category='linear',
                    symbol=symbol,
                    side='Sell',
                    orderType='Market',
                    qty=order_qty,
                    takeProfit=tp_price,
                    stopLoss=sl_price,
                    # tpTriggerBy='Market',
                    # slTriggerBy='Market'
                )
                print(f'Takeprofit: {tp_price}')
                print(f'Stoploss: {sl_price}')
                print(resp['retMsg'])
                return resp['retMsg']
            else:
                print("Invalid side specified. Use 'buy' or 'sell'.")

        except Exception as err:
            print(err)

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