def calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward, is_sell=False):
    """
    Calculate take profit and stop loss based on ATR-derived stop distance and risk:reward ratio
    
    Args:
        entry_price: Current market price
        stop_loss_distance: Distance to stop loss (e.g. from ATR)
        risk_to_reward: Risk to reward ratio (default 2.5)
        is_sell: True for short positions, False for long positions
    """
    # Increase risk:reward ratio for better profitability
    tp_distance = stop_loss_distance * risk_to_reward
    
    # Add buffer to stop loss to avoid premature exits
    buffer = stop_loss_distance * 0.1
    
    if is_sell:
        take_profit = entry_price - tp_distance  # Lower price target for shorts
        stop_loss = entry_price + stop_loss_distance + buffer
    else:
        take_profit = entry_price + tp_distance  # Higher price target for longs 
        stop_loss = entry_price - stop_loss_distance - buffer

    return take_profit, stop_loss


def calculate_tp_sl_by_percent(entry_price, take_profit_percent=0.02, stop_loss_percent=0.01, is_sell=False):
    """
    Calculate take profit and stop loss based on percentage of entry price
    
    Args:
        entry_price: Current market price
        take_profit_percent: Percentage for take profit (default 2.0%)
        stop_loss_percent: Percentage for stop loss (default 0.8%)
        is_sell: True for short positions, False for long positions
    """
    # Increase take profit target while keeping tight stop loss
    if is_sell:
        take_profit = entry_price * (1 - take_profit_percent)
        stop_loss = entry_price * (1 + stop_loss_percent)
    else:
        take_profit = entry_price * (1 + take_profit_percent)
        stop_loss = entry_price * (1 - stop_loss_percent)

    return take_profit, stop_loss
