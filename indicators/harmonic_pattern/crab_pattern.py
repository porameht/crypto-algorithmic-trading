import pandas as pd

def is_crab_pattern(prices):
    XA = prices[1] - prices[0]
    AB = prices[2] - prices[1]
    BC = prices[3] - prices[2]
    CD = prices[4] - prices[3]

    # Fibonacci Ratios for Crab pattern
    AB_XA = abs(AB / XA)
    BC_AB = abs(BC / AB)
    CD_BC = abs(CD / BC)

    is_crab = (0.382 <= AB_XA <= 0.618) and (0.382 <= BC_AB <= 0.886) and (2.618 <= CD_BC <= 3.618)
    
    return is_crab

def get_crab_patterns(data):
    patterns = []
    for i in range(len(data) - 4):
        segment = data['close'].iloc[i:i + 5].values
        if is_crab_pattern(segment):
            patterns.append((data.index[i], data.index[i + 4]))

    return patterns

def scan_crab_patterns(session, symbol, timeframe):
    kl = session.klines(symbol, timeframe)
    data = pd.DataFrame({
        'open': kl.Open,
        'high': kl.High,
        'low': kl.Low,
        'close': kl.Close,
        'volume': kl.Volume
    })

    crab_patterns = get_crab_patterns(data)
    return crab_patterns
