import ta

def moving_averages_signal(kl):
    ema50 = ta.trend.EMAIndicator(kl.Close, window=50).ema_indicator()
    ema200 = ta.trend.EMAIndicator(kl.Close, window=200).ema_indicator()
    if ema50.iloc[-1] > ema200.iloc[-1]:
        return 'buy'
    elif ema50.iloc[-1] < ema200.iloc[-1]:
        return 'sell'
    else:
        return 'none'
