import ta
from indicators.calculate_tp_sl import calculate_tp_sl
from common.enums import Signal
from TelegramBot import TelegramBot

def rsi_basic_signal(session, symbol, timeframe, window_rsi=14, window_atr=14, config=None):
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
        telegram = TelegramBot(config)
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
        # Calculate trend percentages
        ema_diff_percent = ((ema_20.iloc[-1] - ema_50.iloc[-1]) / ema_50.iloc[-1]) * 100
            
        # Check conditions for bullish or bearish signal
        if rsi.iloc[-2] < 25 and rsi.iloc[-1] > 25:
            take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward=2.5)
            telegram.send_message(
                f"🟢 {symbol} RSI Alert\n"
                f"RSI: {round(rsi.iloc[-1], 2)}\n"
                f"RSI[-2]: {round(rsi.iloc[-2], 2)}\n"
                f"[-2]<25 && [-1]>25: {'✅' if rsi.iloc[-2] < 25 and rsi.iloc[-1] > 25 else '❌'}\n"
                f"Volume Increase: {'✅' if volume_increase else '❌'}\n"
                f"Uptrend: {'✅' if uptrend else '❌'}\n"
                f"Trend %: {round(ema_diff_percent, 2)}%"
            )
            return Signal.UP.value, take_profit, stop_loss
            
        if rsi.iloc[-2] > 75 and rsi.iloc[-1] < 75:
            take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward=2.5, is_sell=True)
            telegram.send_message(
                f"🔴 {symbol} RSI Alert\n"
                f"RSI: {round(rsi.iloc[-1], 2)}\n"
                f"RSI[-2]: {round(rsi.iloc[-2], 2)}\n"
                f"[-2]>75 && [-1]<75: {'✅' if rsi.iloc[-2] > 75 and rsi.iloc[-1] < 75 else '❌'}\n"
                f"Volume Increase: {'✅' if volume_increase else '❌'}\n" 
                f"Downtrend: {'✅' if downtrend else '❌'}\n"
                f"Trend %: {round(ema_diff_percent, 2)}%"
            )
            return Signal.DOWN.value, take_profit, stop_loss
        
    except Exception as e:
        print(f"Error in rsi_basic_signal for {symbol}: {e}")
        return Signal.NONE.value, None, None