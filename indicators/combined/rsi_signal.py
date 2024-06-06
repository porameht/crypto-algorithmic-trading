import ta

def rsi_signal(kl):
    rsi = ta.momentum.RSIIndicator(kl.Close).rsi()
    if rsi.iloc[-2] < 30 and rsi.iloc[-1] > 30:
        return 'buy'
    if rsi.iloc[-2] > 70 and rsi.iloc[-1] < 70:
        return 'sell'
    else:
        return 'none'
