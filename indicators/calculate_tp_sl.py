def calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward, is_sell=False):
    tp_distance = stop_loss_distance * risk_to_reward
    if is_sell:
        take_profit = entry_price - tp_distance
        stop_loss = entry_price + stop_loss_distance
    else:
        take_profit = entry_price + tp_distance
        stop_loss = entry_price - stop_loss_distance

    return take_profit, stop_loss


def calculate_tp_sl_by_percent(entry_price, is_sell=False):
    take_profit_percent = 0.008
    stop_loss_percent = 0.004
    if is_sell:
        take_profit = entry_price * (1 - take_profit_percent)
        stop_loss = entry_price * (1 + stop_loss_percent)
    else:
        take_profit = entry_price * (1 + take_profit_percent)
        stop_loss = entry_price * (1 - stop_loss_percent)

    return take_profit, stop_loss
