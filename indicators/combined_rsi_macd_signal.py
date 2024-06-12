import ta

def combined_rsi_macd_signal(session, symbol, timeframe):
        
    kl = session.klines(symbol, timeframe)
    
    rsi = ta.momentum.RSIIndicator(kl.Close, window=20).rsi()
    macd = ta.trend.macd_diff(kl.Close)
    
    if rsi.iloc[-1] < 30 and macd.iloc[-1] > 0:
        print(f"📈 Signal: Buy {symbol}")
        return 'up', kl
    elif rsi.iloc[-1] > 70 and macd.iloc[-1] < 0:
        print(f"📉 Signal: Sell {symbol}")
        return 'down', kl
    else:
        return 'none', kl
                