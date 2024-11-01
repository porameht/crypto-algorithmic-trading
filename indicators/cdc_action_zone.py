import ta
import numpy as np
import pandas as pd

def cdc_action_zone(session, symbol):
    # Get klines data with optimized timeframe
    kl = session.klines(symbol, 60)
    close = kl.Close.values  # Convert to numpy array for faster calculations
    volume = kl.Volume.values

    # Optimized EMA periods
    xprd1 = 10  # Faster EMA period
    xprd2 = 21  # Slower EMA period 
    xsmooth = 1

    # Calculate EMAs using numpy's exponential weighted moving average
    xPrice = pd.Series(close).ewm(span=xsmooth, adjust=False).mean().values
    FastMA = pd.Series(xPrice).ewm(span=xprd1, adjust=False).mean().values
    SlowMA = pd.Series(xPrice).ewm(span=xprd2, adjust=False).mean().values

    # Calculate trend conditions using numpy operations
    Bull = FastMA > SlowMA
    Bear = FastMA < SlowMA

    # Volume confirmation using numpy
    vol_ma = pd.Series(volume).rolling(window=20).mean().values
    high_vol = volume > (vol_ma * 1.2)

    # Vectorized signal calculations
    Green = np.logical_and(Bull, np.logical_and(xPrice > FastMA, high_vol))
    Blue = np.logical_and.reduce([Bear, xPrice > FastMA, xPrice > SlowMA, high_vol])
    LBlue = np.logical_and.reduce([Bear, xPrice > FastMA, xPrice < SlowMA, high_vol])

    Red = np.logical_and(Bear, np.logical_and(xPrice < FastMA, high_vol))
    Orange = np.logical_and.reduce([Bull, xPrice < FastMA, xPrice < SlowMA, high_vol])
    Yellow = np.logical_and.reduce([Bull, xPrice < FastMA, xPrice > SlowMA, high_vol])

    return Green, Blue, LBlue, Red, Orange, Yellow

# import ta

# def cdc_action_zone(session, symbol):
#     kl = session.klines(symbol, 60)
#     xsrc = kl.Close
#     xprd1 = 12
#     xprd2 = 26
#     xsmooth = 1

#     xPrice = ta.trend.EMAIndicator(xsrc, window=xsmooth).ema_indicator()
#     FastMA = ta.trend.EMAIndicator(xPrice, window=xprd1).ema_indicator()
#     SlowMA = ta.trend.EMAIndicator(xPrice, window=xprd2).ema_indicator()

#     Bull = FastMA > SlowMA
#     Bear = FastMA < SlowMA

#     Green = Bull & (xPrice > FastMA)
#     Blue = Bear & (xPrice > FastMA) & (xPrice > SlowMA)
#     LBlue = Bear & (xPrice > FastMA) & (xPrice < SlowMA)

#     Red = Bear & (xPrice < FastMA)
#     Orange = Bull & (xPrice < FastMA) & (xPrice < SlowMA)
#     Yellow = Bull & (xPrice < FastMA) & (xPrice > SlowMA)

#     return Green, Blue, LBlue, Red, Orange, Yellow