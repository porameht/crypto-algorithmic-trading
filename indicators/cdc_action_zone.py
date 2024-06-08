import ta

def cdc_action_zone(session, symbol, timeframe, fast_period=12, slow_period=26, smoothing_period=1):
    kl = session.klines(symbol, timeframe)
    price = kl.Close
    
    fast_ema = ta.trend.EMAIndicator(price, window=fast_period).ema_indicator()
    slow_ema = ta.trend.EMAIndicator(price, window=slow_period).ema_indicator()
    smoothed_price = ta.trend.EMAIndicator(price, window=smoothing_period).ema_indicator()
    
    bull = fast_ema > slow_ema
    bear = fast_ema < slow_ema

    green = bull and smoothed_price > fast_ema  # Buy
    red = bear and smoothed_price < fast_ema    # Sell

    buy_signal = green and not green.shift(1).fillna(False)
    sell_signal = red and not red.shift(1).fillna(False)

    if buy_signal.iloc[-1]:
        print(f'📈 Buy signal for {symbol}')
        return 'buy'
    elif sell_signal.iloc[-1]:
        print(f'📉 Sell signal for {symbol}')
        return 'sell'
    else:
        return 'none'
