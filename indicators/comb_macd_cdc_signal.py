from common.enums import Signal
from indicators.cdc_action_zone import cdc_action_zone
from indicators.macd_signal import macd_signal

def comb_macd_cdc_signal(session, symbol, timeframe):
    kl = session.klines(symbol, timeframe)
    entry_price = kl.Close.iloc[-1]

    # Combine RSI, MACD, MA, and CDC Action Zone logic
    signal, take_profit, stop_loss = macd_signal(session, symbol, timeframe)

    Green, Blue, LBlue, Red, Orange, Yellow = cdc_action_zone(session, symbol)
    
    if signal == Signal.UP.value and Green.iloc[-1]:
        return Signal.UP.value, take_profit, stop_loss
    elif signal == Signal.DOWN.value and Red.iloc[-1]:
        return Signal.DOWN.value, take_profit, stop_loss
    else:
        return Signal.NONE.value, None, None
