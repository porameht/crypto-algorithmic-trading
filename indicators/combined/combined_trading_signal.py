import ta
from indicators.combined.moving_averages_signal import moving_averages_signal
from indicators.combined.rsi_signal import rsi_signal
from indicators.combined.macd_signal import macd_signal
from indicators.combined.bollinger_bands import bollinger_bands_signal
from indicators.combined.volume_analysis import volume_signal

def combined_trading_signal(session, symbol, timeframe):
    kl = session.klines(symbol, timeframe)
    
    # Generate individual signals
    ma_signal = moving_averages_signal(kl)
    rsi_signal_value = rsi_signal(kl)
    macd_signal_value = macd_signal(kl)
    bb_signal = bollinger_bands_signal(kl)
    vol_signal = volume_signal(kl)
    
    # Combine signals (simple example of majority voting)
    signals = [ma_signal, rsi_signal_value, macd_signal_value, bb_signal, vol_signal]
    buy_signals = signals.count('buy')
    sell_signals = signals.count('sell')
    
    final_signal = 'none'
    if buy_signals > sell_signals:
        final_signal = 'up'
    elif sell_signals > buy_signals:
        final_signal = 'down'
    
    return final_signal
