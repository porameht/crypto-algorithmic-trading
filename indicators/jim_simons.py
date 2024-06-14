import ta

# def get_dax_ema_cross_signal(kl):
#     ema_short = ta.trend.EMAIndicator(kl.Close, window=12).ema_indicator()
#     ema_long = ta.trend.EMAIndicator(kl.Close, window=26).ema_indicator()
    
#     if ema_short.iloc[-1] > ema_long.iloc[-1] and ema_short.iloc[-2] <= ema_long.iloc[-2]:
#         return 'buy'
#     elif ema_short.iloc[-1] < ema_long.iloc[-1] and ema_short.iloc[-2] >= ema_long.iloc[-2]:
#         return 'sell'
#     else:
#         return 'none'

def get_dax_ema_cross_signal(kl):
    # Calculate the short and long EMAs
    ema_short = ta.trend.EMAIndicator(kl.Close, window=12).ema_indicator()
    ema_long = ta.trend.EMAIndicator(kl.Close, window=26).ema_indicator()
    
    # Determine if a cross has occurred
    cross_up = (ema_short.iloc[-1] > ema_long.iloc[-1]) and (ema_short.iloc[-2] <= ema_long.iloc[-2])
    cross_down = (ema_short.iloc[-1] < ema_long.iloc[-1]) and (ema_short.iloc[-2] >= ema_long.iloc[-2])
    
    # Return the signal
    if cross_up:
        return 'buy'
    elif cross_down:
        return 'sell'
    else:
        return 'none'
      
def get_rsi_bb_ema_dispersion_signal(kl):
    stdev_mult = 3
    dispersion = 0.1
    
    close = kl.Close
    rsi = ta.momentum.RSIIndicator(close, window=12).rsi()
    basis = ta.trend.EMAIndicator(rsi, window=21).ema_indicator()
    stdev = rsi.rolling(window=21).std()
    
    upper = basis + stdev_mult * stdev
    lower = basis - stdev_mult * stdev
    disp_up = basis + ((upper - lower) * dispersion)
    disp_down = basis - ((upper - lower) * dispersion)
    
    if rsi.iloc[-1] >= disp_up.iloc[-1]:
        return 'sell'
    elif rsi.iloc[-1] <= disp_down.iloc[-1]:
        return 'buy'
    else:
        return 'none'


# def get_rsi_bb_ema_signal(kl):
#     rsi = ta.momentum.RSIIndicator(kl.Close, window=12).rsi()
#     bb = ta.volatility.BollingerBands(kl.Close, window=21, window_dev=3)
#     bb_upper = bb.bollinger_hband()
#     bb_lower = bb.bollinger_lband()
#     ema = ta.trend.EMAIndicator(kl.Close, window=21).ema_indicator()
    
#     if rsi.iloc[-1] > 70 and kl.Close.iloc[-1] > bb_upper.iloc[-1]:
#         return 'sell'
#     elif rsi.iloc[-1] < 30 and kl.Close.iloc[-1] < bb_lower.iloc[-1]:
#         return 'buy'
#     else:
#         return 'none'

# def calculate_tp_sl(entry_price, stop_loss, risk_to_reward=1.5):
#     tp = entry_price + (entry_price - stop_loss) * risk_to_reward
#     return tp, stop_loss

def calculate_tp_sl(entry_price, stop_loss, direction, risk_to_reward=1.5):
    stop_loss_distance = abs(entry_price - stop_loss)
    tp_distance = stop_loss_distance * risk_to_reward
    if direction == 'long':
        take_profit = entry_price + tp_distance
    else:
        take_profit = entry_price - tp_distance
    
    return take_profit, stop_loss


def jim_simons_signal(session, symbol, timeframe):
    kl = session.klines(symbol, timeframe)
    
    dax_signal = get_dax_ema_cross_signal(kl)
    rsi_bb_signal = get_rsi_bb_ema_dispersion_signal(kl)
    
    if dax_signal == 'buy' and rsi_bb_signal == 'buy' and kl.Close.iloc[-1] > kl.Open.iloc[-1]:
        entry_price = kl.Close.iloc[-1]
        stop_loss = min(ta.trend.EMAIndicator(kl.Close, window=12).ema_indicator().iloc[-1],
                        ta.trend.EMAIndicator(kl.Close, window=26).ema_indicator().iloc[-1])
        take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss, risk_to_reward=1.5, direction='long')
        return 'up', take_profit, stop_loss
    elif dax_signal == 'sell' and rsi_bb_signal == 'sell' and kl.Close.iloc[-1] < kl.Open.iloc[-1]:
        entry_price = kl.Close.iloc[-1]
        stop_loss = max(ta.trend.EMAIndicator(kl.Close, window=12).ema_indicator().iloc[-1],
                        ta.trend.EMAIndicator(kl.Close, window=26).ema_indicator().iloc[-1])
        take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss, risk_to_reward=1.5, direction='short')
        return 'down', take_profit, stop_loss
    else:
        return 'none', None, None
