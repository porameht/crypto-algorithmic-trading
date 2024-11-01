import ta
from indicators.macd_signal import macd_signal
from indicators.rsi_basic_signal import rsi_basic_signal
from common.enums import Signal

def comb_rsi_macd_signal(session, symbol, timeframe, window_rsi=14, window_atr=14):
    """
    Combines RSI and MACD signals to generate trading signals.
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
        
        macd_signal_result, macd_tp, macd_sl = macd_signal(
            session,
            symbol,
            timeframe
        )

        if rsi_signal == Signal.UP.value and macd_signal_result == Signal.UP.value:
            return Signal.UP.value, rsi_tp, rsi_sl
        elif rsi_signal == Signal.DOWN.value and macd_signal_result == Signal.DOWN.value:
            return Signal.DOWN.value, rsi_tp, rsi_sl

        return Signal.NONE.value, None, None
        
    except Exception as e:
        print(f"Error in comb_rsi_macd_signal for {symbol}: {e}")
        return Signal.NONE.value, None, None
