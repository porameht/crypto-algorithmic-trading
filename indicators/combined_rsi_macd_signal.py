import ta
from indicators.adjust_take_profit_stop_loss import calculate_tp_sl
from indicators.cdc_action_zone import cdc_action_zone

def combined_rsi_macd_signal(session, symbol, timeframe):
    kl = session.klines(symbol, timeframe)
    entry_price = kl.Close.iloc[-1]

    # Adjusted RSI window to 14
    rsi = ta.momentum.RSIIndicator(kl.Close, window=14).rsi()
    macd = ta.trend.MACD(kl.Close).macd_diff()
    atr = ta.volatility.AverageTrueRange(kl.High, kl.Low, kl.Close, window=20).average_true_range()

    stop_loss_distance = round(atr.iloc[-1], session.get_precisions(symbol)[0])

    # Additional trend filter using 50-period moving average
    # ma = ta.trend.SMAIndicator(kl.Close, window=50).sma_indicator()
    if rsi.iloc[-2] < 30 and rsi.iloc[-1] > 30 and macd.iloc[-1] > 0:
        take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward=2.0)
        return 'up', take_profit, stop_loss
    elif rsi.iloc[-2] > 70 and rsi.iloc[-1] < 70 and macd.iloc[-1] < 0:
        take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward=2.0, is_sell=True)
        return 'down', take_profit, stop_loss
    else:
        return 'none', None, None
    
def combined_rsi_macd_cdc_signal(session, symbol, timeframe):
    kl = session.klines(symbol, timeframe)
    entry_price = kl.Close.iloc[-1]

    # Combine RSI, MACD, MA, and CDC Action Zone logic
    signal, take_profit, stop_loss = combined_rsi_macd_signal(session, symbol, timeframe)

    Green, Blue, LBlue, Red, Orange, Yellow = cdc_action_zone(session, symbol)
    if signal == 'up' and Green.iloc[-1]:
        print(f"🥬 Green signal met for {symbol} at {entry_price}.")
        return 'up', take_profit, stop_loss
    elif signal == 'down' and Red.iloc[-1]:
        print(f"🍄 Red signal met for {symbol} at {entry_price}.")
        return 'down', take_profit, stop_loss
    else:
        return 'none', None, None
