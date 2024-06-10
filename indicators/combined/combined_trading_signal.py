import pandas as pd
from indicators.combined.moving_averages_signal import moving_averages_signal
from indicators.combined.rsi_signal import rsi_signal
from indicators.combined.macd_signal import macd_signal
from indicators.combined.bollinger_bands import bollinger_bands_signal
from indicators.combined.volume_analysis import volume_signal


def combined_trading_signal(kl):
    try:
        # Convert the dict values to pandas Series
        data = {k: pd.Series([v]) for k, v in kl.items()}
        
        # Generate individual signals
        ma_signal = moving_averages_signal(data)
        rsi_signal_value = rsi_signal(data)
        macd_signal_value = macd_signal(data)
        bb_signal = bollinger_bands_signal(data)
        vol_signal = volume_signal(data)

        # Logging each signal
        # logger.info(f"MACD Signal: {macd_signal_value}")
        # logger.info(f"Bollinger Bands Signal: {bb_signal}")
        # logger.info(f"Volume Signal: {vol_signal}")
        
        # Combine signals (simple example of majority voting)
        signals = [rsi_signal_value, ma_signal, macd_signal_value, bb_signal, vol_signal]
        
        print(signals)
        buy_signals = signals.count('buy')
        sell_signals = signals.count('sell')
        
        final_signal = 'none'
        if buy_signals > sell_signals:
            final_signal = 'up'
        elif sell_signals > buy_signals:
            final_signal = 'down'
        
        return final_signal
    
    except Exception as e:
        return 'none'
