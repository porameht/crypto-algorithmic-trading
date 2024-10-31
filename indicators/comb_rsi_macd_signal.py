import ta
from indicators.calculate_tp_sl import calculate_tp_sl
from common.enums import Signal

def comb_rsi_macd_signal(session, symbol, timeframe, window_rsi=14, window_atr=14):
    kl = session.klines(symbol, timeframe)
    rsi = ta.momentum.RSIIndicator(kl.Close, window=window_rsi).rsi()
    entry_price = kl.Close.iloc[-1]
    
    # Calculate ATR for dynamic stop loss
    atr = ta.volatility.AverageTrueRange(kl.High, kl.Low, kl.Close, window=window_atr).average_true_range()
    stop_loss_distance = round(atr.iloc[-1] * 1.5, session.get_precisions(symbol)[0])  # Increased ATR multiplier

    # Add volume confirmation
    volume_increase = kl.Volume.iloc[-1] > kl.Volume.iloc[-2] * 1.1  # 10% volume increase

    # Add trend confirmation using EMA and MACD
    ema_20 = ta.trend.EMAIndicator(kl.Close, window=20).ema_indicator()
    ema_50 = ta.trend.EMAIndicator(kl.Close, window=50).ema_indicator()
    macd = ta.trend.MACD(kl.Close).macd_diff()
    uptrend = ema_20.iloc[-1] > ema_50.iloc[-1] and macd.iloc[-1] > 0
    downtrend = ema_20.iloc[-1] < ema_50.iloc[-1] and macd.iloc[-1] < 0

    # RSI oversold with bullish confirmation
    if rsi.iloc[-2] < 25 and rsi.iloc[-1] > 25 and volume_increase and uptrend:
        take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward=2.5)
        return Signal.UP.value, take_profit, stop_loss

    # RSI overbought with bearish confirmation  
    if rsi.iloc[-2] > 75 and rsi.iloc[-1] < 75 and volume_increase and downtrend:
        take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward=2.5, is_sell=True)
        return Signal.DOWN.value, take_profit, stop_loss

    return Signal.NONE.value, None, None
# def comb_rsi_macd_cdc_signal(session, symbol, timeframe):
#     kl = session.klines(symbol, timeframe)
#     entry_price = kl.Close.iloc[-1]

#     # Combine RSI, MACD, MA, and CDC Action Zone logic
#     signal, take_profit, stop_loss = comb_rsi_macd_signal(session, symbol, timeframe)

#     Green, Blue, LBlue, Red, Orange, Yellow = cdc_action_zone(session, symbol)
#     if signal == 'up' and Green.iloc[-1]:
#         print(f"🥬 Green signal met for {symbol} at {entry_price}.")
#         return 'up', take_profit, stop_loss
#     elif signal == 'down' and Red.iloc[-1]:
#         print(f"🍄 Red signal met for {symbol} at {entry_price}.")
#         return 'down', take_profit, stop_loss
#     else:
#         return 'none', None, None
