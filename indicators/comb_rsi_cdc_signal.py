from common.enums import Signal
from indicators.cdc_action_zone import cdc_action_zone
from indicators.rsi_signal import rsi_signal
from indicators.macd_signal import macd_signal
from TelegramBot import TelegramBot
from indicators.utils import calculate_trend_indicators

def comb_rsi_cdc_signal(session, symbol, timeframe, window_rsi=14, window_atr=14, config=None):
    """
    Combines RSI signal with CDC action zone confirmation.
    Returns signal direction with take profit and stop loss levels.
    """
    try:
        signal_name = 'RSI + CDC + MACD'
        telegram = TelegramBot(config)
        rsi_result, rsi_tp, rsi_sl = rsi_signal(
            session, 
            symbol, 
            timeframe,
            window_rsi,
            window_atr
        )
        
        green, blue, lblue, red, orange, yellow = cdc_action_zone(session, symbol)
        
        macd_signal_result, macd_tp, macd_sl = macd_signal(
            session,
            symbol,
            timeframe
        )
        
        volume_increase, uptrend, downtrend, ema_diff_percent = calculate_trend_indicators(
            session, 
            symbol, 
            timeframe
        )
        
        if rsi_result == Signal.UP.value and green.iloc[-1] and macd_signal_result == Signal.UP.value:
            telegram.send_signal_message(symbol, signal_name, Signal.UP.value, rsi_result, macd_signal_result, volume_increase, uptrend, ema_diff_percent)
            return Signal.UP.value, rsi_tp, rsi_sl
        elif rsi_result == Signal.DOWN.value and red.iloc[-1] and macd_signal_result == Signal.DOWN.value:
            telegram.send_signal_message(symbol, signal_name, Signal.DOWN.value, rsi_result, macd_signal_result, volume_increase, downtrend, ema_diff_percent)
            return Signal.DOWN.value, rsi_tp, rsi_sl

        return Signal.NONE.value, None, None
        
    except Exception as e:
        print(f"Error in comb_rsi_cdc_signal for {symbol}: {e}")
        return Signal.NONE.value, None, None