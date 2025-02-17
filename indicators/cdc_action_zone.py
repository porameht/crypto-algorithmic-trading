import ta
import logging

logger = logging.getLogger(__name__)

def cdc_action_zone(session, symbol):
    kl = session.klines(symbol, 60)
    xsrc = kl.Close
    xprd1 = 12
    xprd2 = 26
    xsmooth = 1

    xPrice = ta.trend.EMAIndicator(xsrc, window=xsmooth).ema_indicator()
    FastMA = ta.trend.EMAIndicator(xPrice, window=xprd1).ema_indicator()
    SlowMA = ta.trend.EMAIndicator(xPrice, window=xprd2).ema_indicator()

    Bull = FastMA > SlowMA
    Bear = FastMA < SlowMA

    Green = Bull & (xPrice > FastMA)
    Blue = Bear & (xPrice > FastMA) & (xPrice > SlowMA)
    LBlue = Bear & (xPrice > FastMA) & (xPrice < SlowMA)

    Red = Bear & (xPrice < FastMA)
    Orange = Bull & (xPrice < FastMA) & (xPrice < SlowMA)
    Yellow = Bull & (xPrice < FastMA) & (xPrice > SlowMA)
    
    # if Green.iloc[-1]:
    #     logger.info(f"🟢 {symbol} CDC signal is UP")
    # elif Red.iloc[-1]:
    #     logger.info(f"🔴 {symbol} CDC signal is DOWN")

    return Green, Blue, LBlue, Red, Orange, Yellow