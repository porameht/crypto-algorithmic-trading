import ta
from indicators.calculate_tp_sl import calculate_tp_sl
from common.enums import Signal

def rsi_basic_signal(session, symbol, timeframe, window_rsi=14, window_atr=14):
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
        if len(kl) < max(window_rsi, window_atr, 50):
            return Signal.NONE.value, None, None
            
        # Calculate indicators
        entry_price = kl.Close.iloc[-1]
        rsi = ta.momentum.RSIIndicator(kl.Close, window=window_rsi).rsi()
        atr = ta.volatility.AverageTrueRange(kl.High, kl.Low, kl.Close, window=window_atr).average_true_range()
        ema_20 = ta.trend.EMAIndicator(kl.Close, window=20).ema_indicator()
        ema_50 = ta.trend.EMAIndicator(kl.Close, window=50).ema_indicator()
        
        # Calculate conditions
        stop_loss_distance = round(atr.iloc[-1] * 1.5, session.get_precisions(symbol)[0])
        volume_increase = kl.Volume.iloc[-1] > kl.Volume.iloc[-2] * 1.1
        uptrend = ema_20.iloc[-1] > ema_50.iloc[-1]
        downtrend = ema_20.iloc[-1] < ema_50.iloc[-1]

        # Generate signals
        if _is_bullish_signal(rsi, volume_increase, uptrend):
            take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward=2.5)
            return Signal.UP.value, take_profit, stop_loss
            
        if _is_bearish_signal(rsi, volume_increase, downtrend):
            take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward=2.5, is_sell=True)
            return Signal.DOWN.value, take_profit, stop_loss
            
        return Signal.NONE.value, None, None
        
    except Exception as e:
        print(f"Error in rsi_basic_signal for {symbol}: {e}")
        return Signal.NONE.value, None, None

def _is_bullish_signal(rsi, volume_increase, uptrend):
    """Check if conditions indicate a bullish signal"""
    return rsi.iloc[-2] < 25 and rsi.iloc[-1] > 25 and volume_increase and uptrend

def _is_bearish_signal(rsi, volume_increase, downtrend):
    """Check if conditions indicate a bearish signal"""
    return rsi.iloc[-2] > 75 and rsi.iloc[-1] < 75 and volume_increase and downtrend