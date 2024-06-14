# import ta

# def combined_rsi_macd_signal(session, symbol, timeframe):
        
#     kl = session.klines(symbol, timeframe)
#     rsi = ta.momentum.RSIIndicator(kl.Close, window=20).rsi()
#     macd = ta.trend.macd_diff(kl.Close)
    
#     if rsi.iloc[-1] < 30 and macd.iloc[-1] > 0:
#         return 'up', kl
#     elif rsi.iloc[-1] > 70 and macd.iloc[-1] < 0:
#         return 'down', kl
#     else:
#         return 'none', kl
                
import ta

from indicators.adjust_take_profit_stop_loss import adjust_take_profit_stop_loss

def calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward=1.5):
    tp_distance = stop_loss_distance * risk_to_reward
    take_profit = entry_price + tp_distance
    stop_loss = entry_price - stop_loss_distance
    return take_profit, stop_loss

def combined_rsi_macd_signal(session, symbol, timeframe):
    kl = session.klines(symbol, timeframe)
    
    rsi = ta.momentum.RSIIndicator(kl.Close, window=20).rsi()
    macd = ta.trend.macd_diff(kl.Close)
    
    entry_price = kl.Close.iloc[-1]

    if rsi.iloc[-2] < 30 and rsi.iloc[-1] > 30 and macd.iloc[-1] > 0:
        take_profit, stop_loss = calculate_tp_sl(entry_price, kl.Close.iloc[-1] * 0.05, risk_to_reward=1.5)
        return 'up', take_profit, stop_loss
    elif rsi.iloc[-2] > 70 and rsi.iloc[-1] < 70 and macd.iloc[-1] < 0:
        take_profit, stop_loss = calculate_tp_sl(entry_price, kl.Close.iloc[-1] * 0.05, risk_to_reward=1.5)
        return 'down', take_profit, stop_loss
    else:
        return 'none', None, None
