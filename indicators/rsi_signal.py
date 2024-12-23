import ta
from indicators.calculate_tp_sl import calculate_tp_sl
from common.enums import Signal
import logging

logger = logging.getLogger(__name__)

def rsi_signal(session, symbol, timeframe, window_rsi=14, window_atr=14, config=None):
    """
    Generate trading signals based on RSI with trend and volume confirmation.
    
    Args:
        session: Trading session object
        symbol: Trading pair symbol
        timeframe: Candlestick timeframe
        window_rsi: RSI calculation period
        window_atr: ATR calculation period
        
    Returns:
        tuple: (signal direction, take profit price, stop loss price)
    """
    try:
        kl = session.klines(symbol, timeframe)
        
        # Check if we have enough data
        if kl is None or len(kl) < max(window_rsi, window_atr, 50):
            logger.warning(f"Insufficient data for RSI calculation for {symbol}")
            return Signal.NONE.value, None, None
            
        # Calculate indicators
        entry_price = kl.Close.iloc[-1]
        rsi = ta.momentum.RSIIndicator(kl.Close, window=window_rsi).rsi()
        
        # Check if RSI calculation failed
        if rsi is None or len(rsi) == 0:
            logger.warning(f"RSI calculation failed for {symbol}")
            return Signal.NONE.value, None, None
            
        atr = ta.volatility.AverageTrueRange(kl.High, kl.Low, kl.Close, window=window_atr).average_true_range()
        # Calculate conditions
        stop_loss_distance = round(atr.iloc[-1] * 1.5, session.get_precisions(symbol)[0])

        print(f"{symbol} 25 {rsi.iloc[-2] < 25 and rsi.iloc[-1] > 25}")
        
        print(f"{symbol} 75 {rsi.iloc[-2] > 75 and rsi.iloc[-1] < 75}")
        
        # Check conditions for bullish or bearish signal
        if rsi.iloc[-2] < 25 and rsi.iloc[-1] > 25:
            logger.info(f"🟢 {symbol} RSI signal is UP")
            take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward=0.5, is_sell=False)
            # return Signal.UP.value, take_profit, stop_loss
            return Signal.DOWN.value, take_profit, stop_loss
            
        if rsi.iloc[-2] > 75 and rsi.iloc[-1] < 75:
            logger.info(f"🔴 {symbol} RSI signal is DOWN")
            take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward=0.5)
            # return Signal.DOWN.value, take_profit, stop_loss
            return Signal.UP.value, take_profit, stop_loss
        
        return Signal.NONE.value, None, None
        
    except Exception as e:
        logger.error(f"Error in rsi_basic_signal for {symbol}: {e}", exc_info=True)
        return Signal.NONE.value, None, None