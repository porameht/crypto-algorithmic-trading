import ta

def bollinger_bands_signal(kl):
    bb = ta.volatility.BollingerBands(kl.Close)
    if kl.Close.iloc[-1] < bb.bollinger_lband().iloc[-1]:
        return 'buy'
    elif kl.Close.iloc[-1] > bb.bollinger_hband().iloc[-1]:
        return 'sell'
    else:
        return 'none'
