import ta
from indicators.adjust_take_profit_stop_loss import calculate_tp_sl

def rsi_basic_signal(session, symbol, timeframe):
    kl = session.klines(symbol, timeframe)
    rsi = ta.momentum.RSIIndicator(kl.Close, window=14).rsi()
    entry_price = kl.Close.iloc[-1]
    
    atr = ta.volatility.AverageTrueRange(kl.High, kl.Low, kl.Close, window=20).average_true_range()
    stop_loss_distance = round(atr.iloc[-1], session.get_precisions(symbol)[0])

    if rsi.iloc[-2] < 30 and rsi.iloc[-1] > 30:
        take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward=2.0)
        return 'up', take_profit, stop_loss
    if rsi.iloc[-2] > 70 and rsi.iloc[-1] < 70:
        take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward=2.0, is_sell=True)
        return 'down', take_profit, stop_loss
    else:
        return 'none', None, None
