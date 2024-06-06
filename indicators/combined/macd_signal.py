import ta

def macd_signal(kl):
    macd = ta.trend.MACD(kl.Close)
    macd_diff = macd.macd_diff().iloc[-1]
    if macd_diff > 0:
        return 'buy'
    elif macd_diff < 0:
        return 'sell'
    else:
        return 'none'
