import ta
from common.enums import Signal
from indicators.calculate_tp_sl import calculate_tp_sl
import logging

logger = logging.getLogger(__name__)

def macd_signal(session, symbol, timeframe):
    try:
        kl = session.klines(symbol, timeframe)
        if len(kl) < 30:  # Ensure we have enough data points
            raise ValueError("Not enough data points")
        
        entry_price = kl.Close.iloc[-1]

        # Custom MACD with (12, 26) settings
        macd_indicator = ta.trend.MACD(kl.Close, window_slow=26, window_fast=12)
        macd_line = macd_indicator.macd()
        macd_signal_line = macd_indicator.macd_signal()

        # Calculate volume indicators
        volume_sma = ta.volume.volume_weighted_average_price(kl.High, kl.Low, kl.Close, kl.Volume, window=20)
        current_volume = kl.Volume.iloc[-1]
        avg_volume = volume_sma.iloc[-1]
        volume_increase = current_volume > (1.5 * avg_volume)  # Volume should be 50% above average

        atr = ta.volatility.AverageTrueRange(kl.High, kl.Low, kl.Close, window=20).average_true_range()
        stop_loss_distance = round(atr.iloc[-1], session.get_precisions(symbol)[0])    

        if macd_line.iloc[-1] > 0 and macd_signal_line.iloc[-1] < 0 and volume_increase:
            logger.info(f"🟢 {symbol} MACD signal is UP")
            take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward=4.0)
            return Signal.UP.value, take_profit, stop_loss
        elif macd_line.iloc[-1] < 0 and macd_signal_line.iloc[-1] > 0 and volume_increase:
            logger.info(f"🔴 {symbol} MACD signal is DOWN")
            take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward=4.0, is_sell=True)
            return Signal.DOWN.value, take_profit, stop_loss
        else:
            return Signal.NONE.value, None, None
    except Exception as e:
        logger.error(f"Error processing {symbol}: {e}", exc_info=True)
        return Signal.NONE.value, None, None