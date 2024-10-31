from common.enums import Signal
from indicators.cdc_action_zone import cdc_action_zone
from indicators.rsi_basic_signal import rsi_basic_signal

def comb_rsi_cdc_signal(session, symbol, timeframe):
    signal, take_profit, stop_loss = rsi_basic_signal(session, symbol, timeframe, 14, 20)
    Green, Blue, LBlue, Red, Orange, Yellow = cdc_action_zone(session, symbol)

    if signal == Signal.UP.value and Green.iloc[-1]:
        return Signal.UP.value, take_profit, stop_loss
    elif signal == Signal.DOWN.value and Red.iloc[-1]:
        return Signal.DOWN.value, take_profit, stop_loss
    else:
        return Signal.NONE.value, None, None