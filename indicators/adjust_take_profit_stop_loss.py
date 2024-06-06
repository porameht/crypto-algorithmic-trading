import ta

# This function adjusts take profit (TP) and stop loss (SL) levels based on the RSI value and market volatility.
def adjust_take_profit_stop_loss(kl):
    # Calculate RSI
    rsi = ta.momentum.RSIIndicator(kl.Close).rsi().iloc[-1]
    
    # Calculate ATR for volatility measurement
    atr = ta.volatility.AverageTrueRange(kl.High, kl.Low, kl.Close).average_true_range().iloc[-1]
    
    # Determine base TP and SL based on ATR (volatility)
    base_tp = atr * 1.5  # A common multiplier for ATR to determine profit targets
    base_sl = atr * 1.0  # A common multiplier for ATR to determine stop losses
    
    # Adjust TP and SL based on RSI
    if rsi > 70:
        tp = base_tp * 0.8  # Lower TP level for overbought conditions
        sl = base_sl * 0.5  # Lower SL level for overbought conditions
    elif rsi < 30:
        tp = base_tp * 1.2  # Higher TP level for oversold conditions
        sl = base_sl * 1.5  # Higher SL level for oversold conditions
    else:
        tp = base_tp  # Default TP level
        sl = base_sl  # Default SL level
    
    return tp, sl
