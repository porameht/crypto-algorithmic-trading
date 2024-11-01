import ta
import numpy as np
import pandas as pd
from common.enums import Signal

def get_dax_ema_cross_signal(kl):
    """Check for EMA crossover signals using 8 and 21 period EMAs"""
    close = pd.Series(kl.Close) if not isinstance(kl.Close, pd.Series) else kl.Close
    
    ema_short = ta.trend.ema_indicator(close, window=8)
    ema_long = ta.trend.ema_indicator(close, window=21)
    
    cross_up = (ema_short.iloc[-1] > ema_long.iloc[-1]) and (ema_short.iloc[-2] <= ema_long.iloc[-2])
    cross_down = (ema_short.iloc[-1] < ema_long.iloc[-1]) and (ema_short.iloc[-2] >= ema_long.iloc[-2])
    
    if cross_up:
        return Signal.UP.value
    elif cross_down:
        return Signal.DOWN.value
    return Signal.NONE.value

def get_rsi_bb_ema_dispersion_signal(kl):
    """Calculate RSI with Bollinger Bands and EMA dispersion for signals"""
    close = pd.Series(kl.Close) if not isinstance(kl.Close, pd.Series) else kl.Close
    
    rsi = ta.momentum.rsi(close, window=9)
    basis = ta.trend.ema_indicator(rsi, window=14)
    stdev = rsi.rolling(window=14).std()
    
    stdev_mult = 2.5
    dispersion = 0.15
    
    upper = basis.iloc[-1] + stdev_mult * stdev.iloc[-1]
    lower = basis.iloc[-1] - stdev_mult * stdev.iloc[-1]
    band_width = upper - lower
    
    disp_up = basis.iloc[-1] + (band_width * dispersion)
    disp_down = basis.iloc[-1] - (band_width * dispersion)
    
    if rsi.iloc[-1] >= disp_up:
        return Signal.DOWN.value
    elif rsi.iloc[-1] <= disp_down:
        return Signal.UP.value
    return Signal.NONE.value

def calculate_tp_sl(entry_price, stop_loss, direction, risk_to_reward=2.5):
    """Calculate take profit and stop loss levels based on risk:reward ratio"""
    stop_loss_distance = abs(entry_price - stop_loss)
    tp_distance = stop_loss_distance * risk_to_reward
    take_profit = entry_price + tp_distance if direction == 'long' else entry_price - tp_distance
    return take_profit, stop_loss

def jim_simons_signal(session, symbol, timeframe):
    """
    Generate trading signals using a combination of:
    - EMA crossovers
    - RSI with Bollinger Bands
    - Volume confirmation
    - Trend confirmation with 200 EMA
    """
    kl = session.klines(symbol, timeframe)
    close = pd.Series(kl.Close) if not isinstance(kl.Close, pd.Series) else kl.Close
    
    # Get component signals
    dax_signal = get_dax_ema_cross_signal(kl)
    rsi_bb_signal = get_rsi_bb_ema_dispersion_signal(kl)
    
    # Confirmations
    volume_increase = kl.Volume.iloc[-1] > kl.Volume.iloc[-2] * 1.2
    ema_200 = ta.trend.ema_indicator(close, window=200)
    strong_trend = close.iloc[-1] > ema_200.iloc[-1]
    
    # Long signal
    if all([
        dax_signal == Signal.UP.value,
        rsi_bb_signal == Signal.UP.value,
        volume_increase,
        strong_trend
    ]):
        entry_price = close.iloc[-1]
        stop_loss = min(kl.Low.iloc[-3:])
        take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss, direction='long')
        return Signal.UP.value, take_profit, stop_loss
        
    # Short signal    
    if all([
        dax_signal == Signal.DOWN.value,
        rsi_bb_signal == Signal.DOWN.value,
        volume_increase,
        not strong_trend
    ]):
        entry_price = close.iloc[-1]
        stop_loss = max(kl.High.iloc[-3:])
        take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss, direction='short')
        return Signal.DOWN.value, take_profit, stop_loss
        
    return Signal.NONE.value, None, None
