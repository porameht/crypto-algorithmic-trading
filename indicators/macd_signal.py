import ta
from indicators.adjust_take_profit_stop_loss import calculate_tp_sl

def macd_signal(session, symbol, timeframe):
    try:
        kl = session.klines(symbol, timeframe)
        if len(kl) < 30:  # Ensure we have enough data points
            raise ValueError("Not enough data points")
        
        entry_price = kl.Close.iloc[-1]

        # Custom MACD with (12, 26) settings
        macd_indicator = ta.trend.MACD(kl.Close, window_slow=26, window_fast=12)
        macd_line = macd_indicator.macd()
        macd_signal_line = macd_indicator.macd_signal()

        atr = ta.volatility.AverageTrueRange(kl.High, kl.Low, kl.Close, window=20).average_true_range()
        stop_loss_distance = round(atr.iloc[-1], session.get_precisions(symbol)[0])    

        if macd_line.iloc[-1] > 0 and macd_signal_line.iloc[-1] < 0:
            take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward=2.0)
            return 'up', take_profit, stop_loss
        elif macd_line.iloc[-1] < 0 and macd_signal_line.iloc[-1] > 0:
            take_profit, stop_loss = calculate_tp_sl(entry_price, stop_loss_distance, risk_to_reward=2.0, is_sell=True)
            return 'down', take_profit, stop_loss
        else:
            return 'none', None, None
    except Exception as e:
        print(f"Error processing {symbol}: {e}")
        return 'error', None, None