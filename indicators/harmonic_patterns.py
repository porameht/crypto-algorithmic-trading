# pip install pandas numpy yfinance

import pandas as pd
import numpy as np
import yfinance as yf

def fetch_data(symbol, period='1y', interval='1d'):
    """
    Fetch historical market data for a given symbol.
    """
    df = yf.download(symbol, period=period, interval=interval)
    df.dropna(inplace=True)
    return df

def harmonic_patterns(df):
    """
    Identify harmonic patterns (Bullish and Bearish) in the market data.
    """
    patterns = []
    for i in range(len(df)-4):
        XA = df['Close'][i+1] - df['Close'][i]
        AB = df['Close'][i+2] - df['Close'][i+1]
        BC = df['Close'][i+3] - df['Close'][i+2]
        CD = df['Close'][i+4] - df['Close'][i+3]
        
        # Check for Bullish Pattern
        if 0.618*abs(XA) <= abs(AB) <= 0.786*abs(XA) and \
           0.382*abs(BC) <= abs(CD) <= 0.886*abs(BC):
            patterns.append(('Bullish', df.index[i:i+5]))
        
        # Check for Bearish Pattern
        if 0.786*abs(XA) <= abs(AB) <= 1.13*abs(XA) and \
           0.618*abs(BC) <= abs(CD) <= 1.618*abs(BC):
            patterns.append(('Bearish', df.index[i:i+5]))
    
    return patterns

def main():
    symbol = 'AAPL'
    df = fetch_data(symbol)
    patterns = harmonic_patterns(df)
    
    for pattern in patterns:
        print(f"Pattern: {pattern[0]}")
        print(f"Dates: {pattern[1]}")

if __name__ == "__main__":
    main()
