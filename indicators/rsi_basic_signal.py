import ta
from indicators.adjust_take_profit_stop_loss import adjust_take_profit_stop_loss, calculate_tp_sl

def rsi_basic_signal(session, symbol, timeframe):
    kl = session.klines(symbol, timeframe)
    rsi = ta.momentum.RSIIndicator(kl.Close, window=14).rsi()
    
    if rsi.iloc[-2] < 30 and rsi.iloc[-1] > 30:
        take_profit, stop_loss = adjust_take_profit_stop_loss(kl)
        return 'up', take_profit, stop_loss
    if rsi.iloc[-2] > 70 and rsi.iloc[-1] < 70:
        take_profit, stop_loss = adjust_take_profit_stop_loss(kl)
        return 'down', take_profit, stop_loss
    else:
        return 'none', None, None
