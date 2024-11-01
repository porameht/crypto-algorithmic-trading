from common.enums import Signal
from indicators.cdc_action_zone import cdc_action_zone
from indicators.rsi_basic_signal import rsi_basic_signal

def comb_rsi_cdc_signal(session, symbol, timeframe, window_rsi=14, window_atr=14):
    """
    Combines RSI signal with CDC action zone confirmation.
    Returns signal direction with take profit and stop loss levels.
    """
    try:
        rsi_signal, rsi_tp, rsi_sl = rsi_basic_signal(
            session, 
            symbol, 
            timeframe,
            window_rsi,
            window_atr
        )
        
        green, blue, lblue, red, orange, yellow = cdc_action_zone(session, symbol)

        if rsi_signal == Signal.UP.value and green.iloc[-1]:
            return Signal.UP.value, rsi_tp, rsi_sl
        elif rsi_signal == Signal.DOWN.value and red.iloc[-1]:
            return Signal.DOWN.value, rsi_tp, rsi_sl

        return Signal.NONE.value, None, None
        
    except Exception as e:
        print(f"Error in comb_rsi_cdc_signal for {symbol}: {e}")
        return Signal.NONE.value, None, None