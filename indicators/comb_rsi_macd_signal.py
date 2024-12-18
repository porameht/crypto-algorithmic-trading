import ta
from indicators.macd_signal import macd_signal
from indicators.rsi_signal import rsi_signal
from indicators.utils import calculate_trend_indicators
from common.enums import Signal
import logging
from TelegramBot import TelegramBot

logger = logging.getLogger(__name__)

def comb_rsi_macd_signal(session, symbol, timeframe, window_rsi=14, window_atr=14, config=None):
    """
    Combines RSI and MACD signals to generate trading signals.
    Returns signal direction with take profit and stop loss levels.
    """
    try:
        signal_name = 'RSI + MACD'
        telegram = TelegramBot(config)
        rsi_result, rsi_tp, rsi_sl = rsi_signal(
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
        
        volume_increase, uptrend, downtrend, ema_diff_percent = calculate_trend_indicators(
            session, 
            symbol, 
            timeframe
        )
        
        if rsi_result == Signal.UP.value and macd_signal_result == Signal.UP.value:
            logger.info("⬆ Both RSI and MACD signals are UP")
            telegram.send_signal_message(symbol, signal_name, Signal.UP.value, rsi_result, macd_signal_result, volume_increase, uptrend, ema_diff_percent)
            return Signal.UP.value, rsi_tp, rsi_sl
        elif rsi_result == Signal.DOWN.value and macd_signal_result == Signal.DOWN.value:
            logger.info("⬇ Both RSI and MACD signals are DOWN")
            telegram.send_signal_message(symbol, signal_name, Signal.DOWN.value, macd_signal_result, rsi_result, volume_increase, downtrend, ema_diff_percent)
            return Signal.DOWN.value, rsi_tp, rsi_sl

        return Signal.NONE.value, None, None
        
    except Exception as e:
        print(f"Error in comb_rsi_macd_signal for {symbol}: {e}")
        return Signal.NONE.value, None, None
