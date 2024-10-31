from enum import Enum

class Signal(Enum):
    """Trading signal enumeration"""
    UP = 'up'
    DOWN = 'down'
    NONE = 'none'

class OrderSide(Enum):
    """Order side enumeration"""
    BUY = 'Buy'
    SELL = 'Sell'

class OrderType(Enum):
    """Order type enumeration"""
    MARKET = 'Market'
    LIMIT = 'Limit'

class MarginMode(Enum):
    """Margin mode enumeration"""
    ISOLATED = 1
    CROSS = 0

class TimeFrame(Enum):
    """Trading timeframe enumeration"""
    M1 = '1'
    M3 = '3'
    M5 = '5'
    M15 = '15'
    M30 = '30'
    H1 = '60'
    H4 = '240'
    D1 = 'D'
    W1 = 'W'
    MN1 = 'M'