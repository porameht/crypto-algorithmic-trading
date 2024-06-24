import ta
from indicators.calculate_tp_sl import calculate_tp_sl_by_percent

def rsi_basic_signal(session, symbol, timeframe, window_rsi, window_atr):
    kl = session.klines(symbol, timeframe)
    rsi = ta.momentum.RSIIndicator(kl.Close, window=window_rsi).rsi()
    entry_price = kl.Close.iloc[-1]
    
    atr = ta.volatility.AverageTrueRange(kl.High, kl.Low, kl.Close, window=window_atr).average_true_range()
    stop_loss_distance = round(atr.iloc[-1], session.get_precisions(symbol)[0])

    # stop_loss_percent = stop_loss_distance / entry_price

    if rsi.iloc[-2] < 30 and rsi.iloc[-1] > 30:
        take_profit, stop_loss = calculate_tp_sl_by_percent(entry_price)
        return 'up', take_profit, stop_loss
    if rsi.iloc[-2] > 70 and rsi.iloc[-1] < 70:
        take_profit, stop_loss = calculate_tp_sl_by_percent(entry_price, is_sell=True)
        return 'down', take_profit, stop_loss
    else:
        return 'none', None, None