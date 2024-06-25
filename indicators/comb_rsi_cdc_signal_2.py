from indicators.cdc_action_zone import cdc_action_zone
from indicators.rsi_basic_signal import rsi_basic_signal


def comb_rsi_cdc_signal_2(session, symbol, timeframe):
    kl = session.klines(symbol, timeframe)
    entry_price = kl.Close.iloc[-1]

    # Combine RSI, MACD, MA, and CDC Action Zone logic
    signal, take_profit, stop_loss = rsi_basic_signal(session, symbol, timeframe, 14, 14)
    
    Green, Blue, LBlue, Red, Orange, Yellow = cdc_action_zone(session, symbol)
    
    if signal == 'up':
        return 'up', take_profit, stop_loss
    elif signal == 'down':
        return 'down', take_profit, stop_loss
    else:
        return 'none', None, None