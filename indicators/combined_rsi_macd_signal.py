import ta

from indicators.adjust_take_profit_stop_loss import adjust_take_profit_stop_loss

def calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward=1.5):
    tp_distance = stop_loss_distance * risk_to_reward
    take_profit = entry_price + tp_distance
    stop_loss = entry_price - stop_loss_distance
    return take_profit, stop_loss

def combined_rsi_macd_signal(session, symbol, timeframe):
    kl = session.klines(symbol, timeframe)
    entry_price = kl.Close.iloc[-1]

    rsi = ta.momentum.RSIIndicator(kl.Close, window=20).rsi()
    macd = ta.trend.macd_diff(kl.Close)
    atr = ta.volatility.AverageTrueRange(kl.High, kl.Low, kl.Close, window=20).average_true_range()

    stop_loss_distance = round(atr.iloc[-1], session.get_precisions(symbol)[0])

    if rsi.iloc[-2] < 30 and rsi.iloc[-1] > 30 and macd.iloc[-1] > 0:
        take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward=1.5)
        return 'up', take_profit, stop_loss
    elif rsi.iloc[-2] > 70 and rsi.iloc[-1] < 70 and macd.iloc[-1] < 0:
        take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward=1.5)
        return 'down', take_profit, stop_loss
    else:
        return 'none', None, None
