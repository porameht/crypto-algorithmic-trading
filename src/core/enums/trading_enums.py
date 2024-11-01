from enum import Enum

class Signal(Enum):
    UP = 'buy'
    DOWN = 'sell'
    NONE = 'none'

class OrderSide(Enum):
    BUY = 'Buy'
    SELL = 'Sell'

class OrderType(Enum):
    MARKET = 'Market'
    LIMIT = 'Limit'

class MarginMode(Enum):
    ISOLATED = 'ISOLATED'
    CROSS = 'CROSS'

class TimeFrame(Enum):
    M1 = '1'
    M5 = '5'
    M15 = '15'
    M30 = '30'
    H1 = '60'
    H4 = '240'
    D1 = 'D' 