import ta

def calculate_trend_indicators(session, symbol, timeframe):
    """
    Calculate volume increase and trend indicators
    
  Args:
      session: Trading session object
      symbol: Trading symbol
      timeframe: Timeframe for analysis
      
  Returns:
      tuple: (volume_increase, uptrend, downtrend, ema_diff_percent)
  """
    # Get required data
    kl = session.klines(symbol, timeframe)
    ema_20 = ta.trend.EMAIndicator(kl.Close, window=20).ema_indicator()
    ema_50 = ta.trend.EMAIndicator(kl.Close, window=50).ema_indicator()
    
    # Calculate volume increase
    volume_increase = cal_volume_increase(kl)
    
    # Calculate trend indicators
    uptrend, downtrend = cal_trend_indicators(ema_20, ema_50)
    
    # Calculate trend percentages
    ema_diff_percent = cal_ema_diff_percent(ema_20, ema_50)
    
    return volume_increase, uptrend, downtrend, ema_diff_percent

def cal_volume_increase(kl):
    return kl.Volume.iloc[-1] > kl.Volume.iloc[-2] * 1.1

def cal_trend_indicators(ema_20, ema_50):
    uptrend = ema_20.iloc[-1] > ema_50.iloc[-1]
    downtrend = ema_20.iloc[-1] < ema_50.iloc[-1]
    return uptrend, downtrend

def cal_ema_diff_percent(ema_20, ema_50):
    return ((ema_20.iloc[-1] - ema_50.iloc[-1]) / ema_50.iloc[-1]) * 100