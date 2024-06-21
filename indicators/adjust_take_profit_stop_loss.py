def calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward, is_sell=False):
    tp_distance = stop_loss_distance * risk_to_reward
    if is_sell:
        take_profit = entry_price - tp_distance
        stop_loss = entry_price + stop_loss_distance
    else:
        take_profit = entry_price + tp_distance
        stop_loss = entry_price - stop_loss_distance

    return take_profit, stop_loss