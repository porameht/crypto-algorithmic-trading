import pandas as pd

def is_shark_pattern(prices):
    XA = prices[1] - prices[0]
    AB = prices[2] - prices[1]
    BC = prices[3] - prices[2]
    CD = prices[4] - prices[3]

    # Fibonacci Ratios for Shark pattern
    AB_XA = abs(AB / XA)
    BC_AB = abs(BC / AB)
    CD_BC = abs(CD / BC)

    is_shark = (0.886 <= AB_XA <= 1.13) and (1.618 <= BC_AB <= 2.24) and (0.886 <= CD_BC <= 1.13)
    
    return is_shark

def get_shark_patterns(data):
    patterns = []
    for i in range(len(data) - 4):
        segment = data['close'].iloc[i:i + 5].values
        if is_shark_pattern(segment):
            patterns.append((data.index[i], data.index[i + 4]))

    return patterns

def scan_shark_patterns(session, symbol, timeframe):
    kl = session.klines(symbol, timeframe)
    data = pd.DataFrame({
        'open': kl.Open,
        'high': kl.High,
        'low': kl.Low,
        'close': kl.Close,
        'volume': kl.Volume
    })

    shark_patterns = get_shark_patterns(data)
    return shark_patterns
