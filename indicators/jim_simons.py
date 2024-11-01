import ta
import numpy as np
import pandas as pd
from common.enums import Signal

def get_dax_ema_cross_signal(kl):
    # Convert numpy array to pandas Series if needed
    if not isinstance(kl.Close, pd.Series):
        close = pd.Series(kl.Close)
    else:
        close = kl.Close
        
    # Calculate EMAs using pandas
    ema_short = ta.trend.ema_indicator(close, window=8)
    ema_long = ta.trend.ema_indicator(close, window=21)
    
    # Check last 2 values for crossover
    cross_up = (ema_short.iloc[-1] > ema_long.iloc[-1]) and (ema_short.iloc[-2] <= ema_long.iloc[-2])
    cross_down = (ema_short.iloc[-1] < ema_long.iloc[-1]) and (ema_short.iloc[-2] >= ema_long.iloc[-2])
    
    if cross_up:
        return Signal.UP.value
    elif cross_down:
        return Signal.DOWN.value
    else:
        return Signal.NONE.value
      
def get_rsi_bb_ema_dispersion_signal(kl):
    stdev_mult = 2.5  # Reduced for more signals
    dispersion = 0.15  # Increased for stronger confirmation
    
    # Convert to pandas Series if needed
    if not isinstance(kl.Close, pd.Series):
        close = pd.Series(kl.Close)
    else:
        close = kl.Close
        
    rsi = ta.momentum.rsi(close, window=9)  # Faster RSI period
    basis = ta.trend.ema_indicator(rsi, window=14)  # Faster EMA period
    stdev = rsi.rolling(window=14).std()  # Calculate standard deviation using pandas
    
    upper = basis.iloc[-1] + stdev_mult * stdev.iloc[-1]
    lower = basis.iloc[-1] - stdev_mult * stdev.iloc[-1]
    disp_up = basis.iloc[-1] + ((upper - lower) * dispersion)
    disp_down = basis.iloc[-1] - ((upper - lower) * dispersion)
    
    if rsi.iloc[-1] >= disp_up:
        return Signal.DOWN.value
    elif rsi.iloc[-1] <= disp_down:
        return Signal.UP.value
    else:
        return Signal.NONE.value

def calculate_tp_sl(entry_price, stop_loss, direction, risk_to_reward=2.5):  # Increased R:R ratio
    stop_loss_distance = abs(entry_price - stop_loss)
    tp_distance = stop_loss_distance * risk_to_reward
    if direction == 'long':
        take_profit = entry_price + tp_distance
    else:
        take_profit = entry_price - tp_distance
    
    return take_profit, stop_loss

def jim_simons_signal(session, symbol, timeframe):
    kl = session.klines(symbol, timeframe)
    
    # Add volume confirmation
    volume_increase = kl.Volume.iloc[-1] > kl.Volume.iloc[-2] * 1.2  # 20% volume increase
    
    dax_signal = get_dax_ema_cross_signal(kl)
    rsi_bb_signal = get_rsi_bb_ema_dispersion_signal(kl)
    
    # Add trend confirmation using pandas Series
    if not isinstance(kl.Close, pd.Series):
        close = pd.Series(kl.Close)
    else:
        close = kl.Close
        
    ema_200 = ta.trend.ema_indicator(close, window=200)
    strong_trend = close.iloc[-1] > ema_200.iloc[-1]  # Check if price is above 200 EMA
    
    if dax_signal == Signal.UP.value and rsi_bb_signal == Signal.UP.value and volume_increase and strong_trend:
        entry_price = kl.Close.iloc[-1]
        stop_loss = min(kl.Low.iloc[-3:])  # Use recent swing low for stop loss
        take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss, risk_to_reward=2.5, direction='long')
        return Signal.UP.value, take_profit, stop_loss
        
    elif dax_signal == Signal.DOWN.value and rsi_bb_signal == Signal.DOWN.value and volume_increase and not strong_trend:
        entry_price = kl.Close.iloc[-1]
        stop_loss = max(kl.High.iloc[-3:])  # Use recent swing high for stop loss
        take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss, risk_to_reward=2.5, direction='short')
        return Signal.DOWN.value, take_profit, stop_loss
        
    else:
        return Signal.NONE.value, None, None
