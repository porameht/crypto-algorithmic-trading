import ta

# This function generates a signal based on the Stochastic RSI and the 200-period EMA.
def stochastic_rsi_signal(session, symbol, timeframe):
    kl = session.klines(symbol, timeframe)
    rsi = ta.momentum.RSIIndicator(kl.Close).rsi()
    rsi_k = ta.momentum.StochRSIIndicator(kl.Close).stochrsi_k()
    rsi_d = ta.momentum.StochRSIIndicator(kl.Close).stochrsi_d()
    ema = ta.trend.ema_indicator(kl.Close, window=200)
    if rsi.iloc[-1] < 30 and ema.iloc[-1] < kl.Close.iloc[-1] and rsi_k.iloc[-1] < 20 and rsi_k.iloc[-3] < rsi_d.iloc[-3] and rsi_k.iloc[-2] < rsi_d.iloc[-2] and rsi_k.iloc[-1] > rsi_d.iloc[-1]:
        return 'up'
    if rsi.iloc[-1] > 70 and ema.iloc[-1] > kl.Close.iloc[-1] and rsi_k.iloc[-1] > 80 and rsi_k.iloc[-3] > rsi_d.iloc[-3] and rsi_k.iloc[-2] > rsi_d.iloc[-2] and rsi_k.iloc[-1] < rsi_d.iloc[-1]:
        return 'down'
    else:
        return 'none'
