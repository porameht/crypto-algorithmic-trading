import ta
from indicators.calculate_tp_sl import calculate_tp_sl, calculate_tp_sl_by_percent
from common.enums import Signal

def rsi_basic_signal(session, symbol, timeframe, window_rsi=14, window_atr=14):
    kl = session.klines(symbol, timeframe)
    rsi = ta.momentum.RSIIndicator(kl.Close, window=window_rsi).rsi()
    entry_price = kl.Close.iloc[-1]
    
    # Calculate ATR for dynamic stop loss
    atr = ta.volatility.AverageTrueRange(kl.High, kl.Low, kl.Close, window=window_atr).average_true_range()
    stop_loss_distance = round(atr.iloc[-1] * 1.5, session.get_precisions(symbol)[0])  # Increased ATR multiplier

    # Add volume confirmation
    volume_increase = kl.Volume.iloc[-1] > kl.Volume.iloc[-2] * 1.1  # 10% volume increase

    # Add trend confirmation using EMA
    ema_20 = ta.trend.EMAIndicator(kl.Close, window=20).ema_indicator()
    ema_50 = ta.trend.EMAIndicator(kl.Close, window=50).ema_indicator()
    uptrend = ema_20.iloc[-1] > ema_50.iloc[-1]
    downtrend = ema_20.iloc[-1] < ema_50.iloc[-1]

    # RSI oversold with bullish confirmation
    if rsi.iloc[-2] < 25 and rsi.iloc[-1] > 25 and volume_increase and uptrend:
        take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward=2.5)
        return Signal.UP.value, take_profit, stop_loss

    # RSI overbought with bearish confirmation  
    if rsi.iloc[-2] > 75 and rsi.iloc[-1] < 75 and volume_increase and downtrend:
        take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward=2.5, is_sell=True)
        return Signal.DOWN.value, take_profit, stop_loss

    return Signal.NONE.value, None, None


# import ta
# from indicators.calculate_tp_sl import calculate_tp_sl, calculate_tp_sl_by_percent

# def rsi_basic_signal(session, symbol, timeframe, window_rsi, window_atr):
#     kl = session.klines(symbol, timeframe)
#     rsi = ta.momentum.RSIIndicator(kl.Close, window=window_rsi).rsi()
#     entry_price = kl.Close.iloc[-1]
    
#     atr = ta.volatility.AverageTrueRange(kl.High, kl.Low, kl.Close, window=window_atr).average_true_range()
#     stop_loss_distance = round(atr.iloc[-1], session.get_precisions(symbol)[0])

#     # stop_loss_percent = stop_loss_distance / entry_price

#     if rsi.iloc[-2] < 30 and rsi.iloc[-1] > 30:
#         # take_profit, stop_loss = calculate_tp_sl_by_percent(entry_price)
#         take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward=2.0)

#         return 'up', take_profit, stop_loss
#     if rsi.iloc[-2] > 70 and rsi.iloc[-1] < 70:
#         # take_profit, stop_loss = calculate_tp_sl_by_percent(entry_price, is_sell=True)
#         take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward=2.0, is_sell=True)

#         return 'down', take_profit, stop_loss
#     else:
#         return 'none', None, None