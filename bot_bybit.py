import random
from Bybit import Bybit
from time import sleep
import ta
from threading import Thread
import os
from tqdm import tqdm

api = os.getenv('API_BYBIT', None)
secret = os.getenv('SECRET_BYBIT', None)
accountType = os.getenv('ACCOUNT_TYPE', None)

session = Bybit(api, secret, accountType)

# tp = 0.012  # Take Profit +1.2%
# sl = 0.009  # Stop Loss -0.9%

mode = 1  # 1 - Isolated, 0 - Cross
leverage = 25  # 10x
timeframe = 15 # 15 minutes
timeframes = [15]
qty = 1 # Amount of USDT for one order
max_positions = 30 # max 10 positions

#     return tp, sl
def adjust_tp_sl(rsi):
    # If RSI is over 70, it's considered overbought
    if rsi > 70:
        tp = 0.01  # Lower take profit level for overbought conditions (1% of Price)
        sl = 0.005  # Lower stop loss level for overbought conditions (0.5% of Price)
    # If RSI is under 30, it's considered oversold
    elif rsi < 30:
        tp = 0.015  # Higher take profit level for oversold conditions (1.5% of Price)
        sl = 0.012  # Lower stop loss level for oversold conditions (1.2% of Price)
    else:
        # If RSI is between 30 and 70, it's considered normal
        tp = 0.012  # Default take profit level (1.2% of Price)
        sl = 0.009  # Lower stop loss level (0.9% of Price)
    return tp, sl


def combined_signal(session, symbol):
    signals = []
    
    for timeframe in timeframes:
        
        kl = session.klines(symbol, timeframe)
        
        # Calculate RSI
        rsi = ta.momentum.RSIIndicator(kl.Close).rsi()
        
        # Calculate MACD
        macd = ta.trend.macd_diff(kl.Close)
        
        if rsi.iloc[-2] < 30 and rsi.iloc[-1] > 30 and macd.iloc[-1] > 0:
            signals.append('up')
        elif rsi.iloc[-2] > 70 and rsi.iloc[-1] < 70 and macd.iloc[-1] < 0:
            signals.append('down')
        else:
            signals.append('none')
                
    if all(signal == 'up' for signal in signals):
        print(f'📈 Up signal for {symbol}. Prev RSI: {rsi.iloc[-2]}, Current RSI: {rsi.iloc[-1]}. MACD: {macd.iloc[-1]}')
        return 'up'
    elif all(signal == 'down' for signal in signals):
        print(f'📉 Down signal for {symbol}. Prev RSI: {rsi.iloc[-2]}, Current RSI: {rsi.iloc[-1]}. MACD: {macd.iloc[-1]}')
        return 'down'
    else:
        return 'none'

def rsi_signal_basic(session, symbol):
    kl = session.klines(symbol, timeframe)
    rsi = ta.momentum.RSIIndicator(kl.Close).rsi()
    if rsi.iloc[-2] < 30 and rsi.iloc[-1] > 30:
        return 'up'
    if rsi.iloc[-2] > 70 and rsi.iloc[-1] < 70:
        return 'down'
    else:
    
        return 'none'

def rsi_signal14(session, symbol):
    signals = []
    
    for timeframe in timeframes:
        
        kl = session.klines(symbol, timeframe)
        rsi = ta.momentum.RSIIndicator(kl.Close, window=14).rsi()  # Change 14 to desired period
        if rsi.iloc[-2] < 30 and rsi.iloc[-1] > 30:
            signals.append('up')
        elif rsi.iloc[-2] > 70 and rsi.iloc[-1] < 70:
            signals.append('down')
        else:
            signals.append('none')
                
    if all(signal == 'up' for signal in signals):
        print(f'📈 Up signal for {symbol}. Prev RSI: {rsi.iloc[-2]}, Current RSI: {rsi.iloc[-1]}.')
        return 'up'
    elif all(signal == 'down' for signal in signals):
        print(f'📉 Down signal for {symbol}. Prev RSI: {rsi.iloc[-2]}, Current RSI: {rsi.iloc[-1]}.')
        return 'down'
    else:
        return 'none'
    

def signal2(symbol):
    kl = session.klines(symbol, timeframe)
    ema200 = ta.trend.ema_indicator(kl.Close, window=200)
    if kl.Close.iloc[-1] > kl.Open.iloc[-1]:
        if abs(kl.High.iloc[-1]-kl.Close.iloc[-1]) > abs(kl.Close.iloc[-1] - kl.Open.iloc[-1]) and kl.Close.iloc[-1] < ema200.iloc[-1]:
            return 'sell'
        if abs(kl.Open.iloc[-1] - kl.Low.iloc[-1]) > abs(kl.Close.iloc[-1] - kl.Open.iloc[-1]) and kl.Close.iloc[-1] > ema200.iloc[-1]:
            return 'buy'
    if kl.Close.iloc[-1] < kl.Open.iloc[-1]:
        if abs(kl.High.iloc[-1]-kl.Open.iloc[-1]) > abs(kl.Open.iloc[-1] - kl.Close.iloc[-1]) and kl.Close.iloc[-1] < ema200.iloc[-1]:
            return 'sell'
        if abs(kl.Close.iloc[-1] - kl.Low.iloc[-1]) > abs(kl.Open.iloc[-1] - kl.Open.iloc[-1]) and kl.Close.iloc[-1] > ema200.iloc[-1]:
            return 'buy'
    else:
        return 'none'

# William %R signal
def williamsR(symbol):
    kl = session.klines(symbol, timeframe)
    w = ta.momentum.WilliamsRIndicator(kl.High, kl.Low, kl.Close, lbp=24).williams_r()
    ema_w = ta.trend.ema_indicator(w, window=24)
    if w.iloc[-1] < -99.5:
        return 'up'
    elif w.iloc[-1] > -0.5:
        return 'down'
    elif w.iloc[-1] < -75 and w.iloc[-2] < -75 and w.iloc[-2] < ema_w.iloc[-2] and w.iloc[-1] > ema_w.iloc[-1]:
        return 'up'
    elif w.iloc[-1] > -25 and w.iloc[-2] > -25 and w.iloc[-2] > ema_w.iloc[-2] and w.iloc[-1] < ema_w.iloc[-1]:
        return 'down'
    else:
        return 'none'
    
def macd_ema(symbol):
    kl = session.klines(symbol)
    macd = ta.trend.macd_diff(kl.Close)
    ema = ta.trend.ema_indicator(kl.Close, window=200)
    if macd.iloc[-3] < 0 and macd.iloc[-2] < 0 and macd.iloc[-1] > 0 and ema.iloc[-1] < kl.Close.iloc[-1]:
        return 'up'
    if macd.iloc[-3] > 0 and macd.iloc[-2] > 0 and macd.iloc[-1] < 0 and ema.iloc[-1] > kl.Close.iloc[-1]:
        return 'down'
    else:
        return 'none'


def ema200_50(symbol):
    kl = session.klines(symbol)
    ema200 = ta.trend.ema_indicator(kl.Close, window=100)
    ema50 = ta.trend.ema_indicator(kl.Close, window=50)
    if ema50.iloc[-3] < ema200.iloc[-3] and ema50.iloc[-2] < ema200.iloc[-2] and ema50.iloc[-1] > ema200.iloc[-1]:
        return 'up'
    if ema50.iloc[-3] > ema200.iloc[-3] and ema50.iloc[-2] > ema200.iloc[-2] and ema50.iloc[-1] < ema200.iloc[-1]:
        return 'down'
    else:
        return 'none'
    
    
def str_signal(symbol):
    kl = session.klines(symbol)
    rsi = ta.momentum.RSIIndicator(kl.Close).rsi()
    rsi_k = ta.momentum.StochRSIIndicator(kl.Close).stochrsi_k()
    rsi_d = ta.momentum.StochRSIIndicator(kl.Close).stochrsi_d()
    ema = ta.trend.ema_indicator(kl.Close, window=200)
    if rsi.iloc[-1] < 40 and ema.iloc[-1] < kl.Close.iloc[-1] and rsi_k.iloc[-1] < 20 and rsi_k.iloc[-3] < rsi_d.iloc[-3] and rsi_k.iloc[-2] < rsi_d.iloc[-2] and rsi_k.iloc[-1] > rsi_d.iloc[-1]:
        return 'up'
    if rsi.iloc[-1] > 60 and ema.iloc[-1] > kl.Close.iloc[-1] and rsi_k.iloc[-1] > 80 and rsi_k.iloc[-3] > rsi_d.iloc[-3] and rsi_k.iloc[-2] > rsi_d.iloc[-2] and rsi_k.iloc[-1] < rsi_d.iloc[-1]:
        return 'down'

    else:
        return 'none'

symbols = session.get_tickers()

while True:
    balance = session.get_balance()
    
    if balance is None or symbols is None:
        print('Cant connect')
        sleep(120)
    if balance is not None and symbols is not None:
        print(f'Account balance: {balance} USDT')
        print(f'Timeframe: {timeframe} minutes')
        
        try:
            positions = session.get_positions()
            print(f'Opened positions: {len(positions)}')
            last_pnl = session.get_last_pnl(10)
            print(f'Last 10 PnL: {last_pnl} USDT')
            current_pnl = session.get_current_pnl()
            print(f'Current PnL: {current_pnl} USDT')
            for elem in symbols:
                positions = session.get_positions()
                if len(positions) >= max_positions:
                    break
                signal = rsi_signal14(session, elem)
                
                if signal == 'up' and not elem in positions:
                    print(f'Found BUY signal for {elem}')
                    kl = session.klines(elem, timeframe)
                    rsi = ta.momentum.RSIIndicator(kl.Close).rsi().iloc[-1]
                    tp, sl = adjust_tp_sl(rsi)
                    session.place_order_market(elem, 'buy', mode, leverage, qty, tp, sl)
                    sleep(1)
                if signal == 'down' and not elem in positions:
                    print(f'Found SELL signal for {elem}')
                    kl = session.klines(elem, timeframe)
                    rsi = ta.momentum.RSIIndicator(kl.Close).rsi().iloc[-1]
                    tp, sl = adjust_tp_sl(rsi)
                    session.place_order_market(elem, 'sell', mode, leverage, qty, tp, sl)
                    sleep(1)

        except Exception as err:
            print(err)
            print('No connection')
            for i in tqdm(range(60, 0, -1)):
                sleep(1)

    for i in tqdm(range(100, 0, -5)):
        sleep(1)


