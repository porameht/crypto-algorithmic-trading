# import ta

# # This function adjusts take profit (TP) and stop loss (SL) levels based on the RSI value.
# def adjust_take_profit_stop_loss(kl):
#     # Calculate RSI
#     rsi = ta.momentum.RSIIndicator(kl.Close).rsi().iloc[-1]
    
#     # Define base TP and SL levels
#     base_tp = 0.01  # Define a base TP level, e.g., 1%
#     base_sl = 0.005  # Define a base SL level, e.g., 0.5%
    
#     # Adjust TP and SL based on RSI
#     if rsi > 70:
#         tp = base_tp * 0.8  # Lower TP level for overbought conditions
#         sl = base_sl * 0.5  # Lower SL level for overbought conditions
#     elif rsi < 30:
#         tp = base_tp * 1.2  # Higher TP level for oversold conditions
#         sl = base_sl * 1.5  # Higher SL level for oversold conditions
#     else:
#         tp = base_tp  # Default TP level
#         sl = base_sl  # Default SL level
    
#     return tp, sl


# import ta

# def adjust_take_profit_stop_loss(kl):
#     # rsi = ta.momentum.RSIIndicator(kl.Close).rsi().iloc[-1]
    
#     rsi = ta.momentum.RSIIndicator(kl.Close, window=20).rsi()
#     macd = ta.trend.macd_diff(kl.Close)

#     if rsi.iloc[-1] > 70 and macd.iloc[-1] < 0:
#         tp = 0.08  # Lower TP level for overbought conditions
#         sl = 0.05  # Lower SL level for overbought conditions
#     elif rsi.iloc[-1] < 30 and macd.iloc[-1] > 0:
#         tp = 0.18  # Higher TP level for oversold conditions
#         sl = 0.15  # Higher SL level for oversold conditions
#     else:
#         tp = 0.12  # Default TP level
#         sl = 0.08  # Default SL level
    
#     return tp, sl

# import ta

# # This function adjusts take profit (TP) and stop loss (SL) levels based on the RSI value.
# def adjust_take_profit_stop_loss(kl):
#     # Calculate RSI
#     rsi = ta.momentum.RSIIndicator(kl.Close).rsi().iloc[-1]
    
#     # Define base TP and SL levels
#     base_tp = 0.01  # Define a base TP level, e.g., 1%
#     base_sl = 0.005  # Define a base SL level, e.g., 0.5%
    
#     # Adjust TP and SL based on RSI
#     if rsi > 70:
#         tp = base_tp * 0.8  # Lower TP level for overbought conditions
#         sl = base_sl * 0.5  # Lower SL level for overbought conditions
#     elif rsi < 30:
#         tp = base_tp * 1.2  # Higher TP level for oversold conditions
#         sl = base_sl * 1.5  # Higher SL level for oversold conditions
#     else:
#         tp = base_tp  # Default TP level
#         sl = base_sl  # Default SL level
    
#     return tp, sl


import ta

def adjust_take_profit_stop_loss(kl):
    rsi = ta.momentum.RSIIndicator(kl.Close, window=20).rsi()
    macd = ta.trend.macd_diff(kl.Close)

    if rsi.iloc[-1] > 70 and macd.iloc[-1] < 0:
        tp = 0.01  # Lower TP level for overbought conditions
        sl = 0.005  # Lower SL level for overbought conditions
    elif rsi.iloc[-1] < 30 and macd.iloc[-1] > 0:
        tp = 0.02  # Higher TP level for oversold conditions
        sl = 0.01  # Higher SL level for oversold conditions
    else:
        tp = 0.016  # Default TP level
        sl = 0.008  # Default SL level
    
    return tp, sl

def calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward, is_sell=False):
    tp_distance = stop_loss_distance * risk_to_reward
    if is_sell:
        take_profit = entry_price - tp_distance
        stop_loss = entry_price + stop_loss_distance
    else:
        take_profit = entry_price + tp_distance
        stop_loss = entry_price - stop_loss_distance

    return take_profit, stop_loss