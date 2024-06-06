import ta

def volume_signal(kl):
    obv = ta.volume.OnBalanceVolumeIndicator(kl.Close, kl.Volume).on_balance_volume()
    if obv.iloc[-1] > obv.iloc[-2]:
        return 'buy'
    elif obv.iloc[-1] < obv.iloc[-2]:
        return 'sell'
    else:
        return 'none'
