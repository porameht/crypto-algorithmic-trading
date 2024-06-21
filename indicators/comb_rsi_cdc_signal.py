from indicators.cdc_action_zone import cdc_action_zone
from indicators.rsi_basic_signal import rsi_basic_signal
    
def comb_rsi_cdc_signal(session, symbol, timeframe):
    kl = session.klines(symbol, timeframe)
    entry_price = kl.Close.iloc[-1]

    # Combine RSI, MACD, MA, and CDC Action Zone logic
    signal, take_profit, stop_loss = rsi_basic_signal(session, symbol, timeframe)
    
    Green, Blue, LBlue, Red, Orange, Yellow = cdc_action_zone(session, symbol)
    
    if signal == 'up' and Green.iloc[-1]:
        print(f"🥬 Green signal met for {symbol} at {entry_price}.")
        return 'up', take_profit, stop_loss
    elif signal == 'down' and Red.iloc[-1]:
        print(f"🍄 Red signal met for {symbol} at {entry_price}.")
        return 'down', take_profit, stop_loss
    else:
        return 'none', None, None
