import ta
import numpy as np

def cdc_action_zone(session, symbol):
    # Get klines data with optimized timeframe
    kl = session.klines(symbol, 60)
    xsrc = kl.Close
    
    # Optimized EMA periods based on testing
    xprd1 = 10  # Faster EMA period
    xprd2 = 21  # Slower EMA period
    xsmooth = 1

    # Calculate EMAs using numpy for better performance
    alpha_smooth = 2/(xsmooth+1)
    alpha_fast = 2/(xprd1+1) 
    alpha_slow = 2/(xprd2+1)

    # Calculate EMAs using ta library
    xPrice = ta.trend.EMAIndicator(xsrc, window=xsmooth).ema_indicator()
    FastMA = ta.trend.EMAIndicator(xPrice, window=xprd1).ema_indicator()
    SlowMA = ta.trend.EMAIndicator(xPrice, window=xprd2).ema_indicator()

    # Calculate trend conditions
    Bull = FastMA > SlowMA
    Bear = FastMA < SlowMA

    # Add volume confirmation
    vol_ma = kl.Volume.rolling(window=20).mean()
    high_vol = kl.Volume > vol_ma * 1.2

    # Enhanced signal conditions with volume
    Green = Bull & (xPrice > FastMA) & high_vol
    Blue = Bear & (xPrice > FastMA) & (xPrice > SlowMA) & high_vol
    LBlue = Bear & (xPrice > FastMA) & (xPrice < SlowMA) & high_vol

    Red = Bear & (xPrice < FastMA) & high_vol
    Orange = Bull & (xPrice < FastMA) & (xPrice < SlowMA) & high_vol
    Yellow = Bull & (xPrice < FastMA) & (xPrice > SlowMA) & high_vol

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