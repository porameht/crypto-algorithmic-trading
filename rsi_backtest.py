import backtrader as bt
import pandas as pd
import ta


class UnderOver(bt.Indicator):
    lines = ('underover',)
    params = dict(data2=20)
    plotinfo = dict(plot=True)

    def __init__(self):
        self.l.underover = self.data < self.p.data2  # data under data2 == 1

class RSIStrategy(bt.Strategy):
    """
    Live strategy demonstration with SMA, RSI indicators
    """
    params = (  # Parameters of the trading system
        ('coin_target', ''),
        ('timeframe', ''),
    )

    def __init__(self):
        """Initialization, adding indicators for each ticker"""
        self.orders = {}  # All orders as a dict, for this particularly trading strategy one ticker is one order
        for d in self.datas:  # Running through all the tickers
            self.orders[d._name] = None  # There is no order for ticker yet

        # creating indicators for each ticker
        self.sma1 = {}
        self.sma2 = {}
        self.sma3 = {}
        self.crossover = {}
        self.underover_sma = {}
        self.rsi = {}
        self.underover_rsi = {}
        self.rsi_data = {}
        for i in range(len(self.datas)):
            ticker = list(self.dnames.keys())[i]  # key name is ticker name
            self.sma1[ticker] = bt.indicators.SMA(self.datas[i], period=9)  # SMA1 indicator
            self.sma2[ticker] = bt.indicators.SMA(self.datas[i], period=30)  # SMA2 indicator
            self.sma3[ticker] = bt.indicators.SMA(self.datas[i], period=60)  # SMA3 indicator

            # signal 1 - intersection of a fast SMA from bottom to top of a slow SMA
            self.crossover[ticker] = bt.ind.CrossOver(self.sma1[ticker], self.sma2[ticker])  # crossover SMA1 and SMA2

            # signal 2 - when SMA3 is below SMA2
            self.underover_sma[ticker] = UnderOver(self.sma3[ticker].lines.sma, data2=self.sma2[ticker].lines.sma)

            # Creating a placeholder for RSI values
            self.rsi_data[ticker] = []

    def next(self):
        """Arrival of a new ticker candle"""
        for data in self.datas:  # Running through all the requested bars of all tickers
            ticker = data._name
            status = data._state  # 0 - Live data, 1 - History data, 2 - None
            _interval = self.p.timeframe

            if status in [0, 1]:
                if status: _state = "False - History data"
                else: _state = "True - Live data"

                print('{} / {} [{}] - Open: {}, High: {}, Low: {}, Close: {}, Volume: {} - Live: {}'.format(
                    bt.num2date(data.datetime[0]),
                    data._name,
                    _interval,  # ticker timeframe
                    data.open[0],
                    data.high[0],
                    data.low[0],
                    data.close[0],
                    data.volume[0],
                    _state,
                ))

                # Collect close prices to calculate RSI
                self.rsi_data[ticker].append(data.close[0])
                if len(self.rsi_data[ticker]) >= 20:
                    # Convert to Pandas Series and calculate RSI using 'ta' library
                    close_series = pd.Series(self.rsi_data[ticker])
                    rsi_values = ta.momentum.RSIIndicator(close_series, window=20).rsi()
                    current_rsi = rsi_values.iloc[-1]

                    print(f'\t - RSI =', current_rsi)
                    print(f"\t - crossover =", self.crossover[ticker].lines.crossover[0])

                    coin_target = self.p.coin_target
                    print(f"\t - Free balance: {self.broker.getcash()} {coin_target}")

                    # signals to open position
                    signal1 = self.crossover[ticker].lines.crossover[0]  # signal 1 - intersection of a fast SMA from bottom to top of a slow SMA
                    signal2 = self.underover_sma[ticker]  # signal 2 - when SMA3 is below SMA2

                    # signals to close position
                    signal3 = current_rsi < 30  # signal 3 - when the RSI is below 30

                    if not self.getposition(data):  # If there is no position
                        if signal1 == 1:
                            if signal2 == 1:
                                # buy
                                free_money = self.broker.getcash()
                                price = data.close[0]  # by closing price
                                size = (free_money / price) * 0.25  # 25% of available funds
                                print("-" * 50)
                                print(f"\t - buy {ticker} size = {size} at price = {price}")
                                self.orders[data._name] = self.buy(data=data, exectype=bt.Order.Limit, price=price, size=size)
                                print(f"\t - Order has been submitted {self.orders[data._name].p.tradeid} to buy {data._name}")
                                print("-" * 50)

                    else:  # If there is a position
                        if signal3:
                            # sell
                            print("-" * 50)
                            print(f"\t - Sell by market {data._name}...")
                            self.orders[data._name] = self.close()  # Request to close a position at the market price
                            print("-" * 50)

    def notify_order(self, order):
        """Changing the status of the order"""
        print("*" * 50)
        order_data_name = order.data._name  # Name of ticker from order
        self.log(f'Order number {order.ref} {order.info["order_number"]} {order.getstatusname()} {"Buy" if order.isbuy() else "Sell"} {order_data_name} {order.size} @ {order.price}')
        if order.status == bt.Order.Completed:  # If the order is fully executed
            if order.isbuy():  # The order to buy
                self.log(f'Buy {order_data_name} @{order.executed.price:.2f}, Price {order.executed.value:.2f}, Commission {order.executed.comm:.2f}')
            else:  # The order to sell
                self.log(f'Sell {order_data_name} @{order.executed.price:.2f}, Price {order.executed.value:.2f}, Commission {order.executed.comm:.2f}')
                self.orders[order_data_name] = None  # Reset the order to enter the position
        print("*" * 50)

    def notify_trade(self, trade):
        """Changing the position status"""
        if trade.isclosed:  # If the position is closed
            self.log(f'Profit on a closed position {trade.getdataname()} Total={trade.pnl:.2f}, No commission={trade.pnlcomm:.2f}')

    def log(self, txt, dt=None):
        """Print string with date to the console"""
        dt = bt.num2date(self.datas[0].datetime[0]) if not dt else dt  # date or date of the current bar
        print(f'{dt.strftime("%d.%m.%Y %H:%M")}, {txt}')  # Print the date and time with the specified text to the console

class RSIMACDStrategy(bt.Strategy):
    """
    Live strategy demonstration with SMA, RSI, and MACD indicators
    """
    params = (  # Parameters of the trading system
        ('coin_target', ''),
        ('timeframe', ''),
    )

    def __init__(self):
        """Initialization, adding indicators for each ticker"""
        self.orders = {}  # All orders as a dict, for this particularly trading strategy one ticker is one order
        for d in self.datas:  # Running through all the tickers
            self.orders[d._name] = None  # There is no order for ticker yet

        # creating indicators for each ticker
        self.sma1 = {}
        self.sma2 = {}
        self.sma3 = {}
        self.crossover = {}
        self.underover_sma = {}
        self.rsi = {}
        self.underover_rsi = {}
        self.rsi_data = {}
        self.macd = {}
        self.macd_signal = {}
        self.macd_hist = {}
        for i in range(len(self.datas)):
            ticker = list(self.dnames.keys())[i]  # key name is ticker name
            self.sma1[ticker] = bt.indicators.SMA(self.datas[i], period=9)  # SMA1 indicator
            self.sma2[ticker] = bt.indicators.SMA(self.datas[i], period=30)  # SMA2 indicator
            self.sma3[ticker] = bt.indicators.SMA(self.datas[i], period=60)  # SMA3 indicator

            # signal 1 - intersection of a fast SMA from bottom to top of a slow SMA
            self.crossover[ticker] = bt.ind.CrossOver(self.sma1[ticker], self.sma2[ticker])  # crossover SMA1 and SMA2

            # signal 2 - when SMA3 is below SMA2
            self.underover_sma[ticker] = UnderOver(self.sma3[ticker].lines.sma, data2=self.sma2[ticker].lines.sma)

            # Creating placeholders for RSI and MACD values
            self.rsi_data[ticker] = []
            self.macd[ticker] = bt.indicators.MACD(self.datas[i])
            self.macd_signal[ticker] = bt.indicators.MACDHisto(self.datas[i])

    def next(self):
        """Arrival of a new ticker candle"""
        for data in self.datas:  # Running through all the requested bars of all tickers
            ticker = data._name
            status = data._state  # 0 - Live data, 1 - History data, 2 - None
            _interval = self.p.timeframe

            if status in [0, 1]:
                if status: _state = "False - History data"
                else: _state = "True - Live data"

                print('{} / {} [{}] - Open: {}, High: {}, Low: {}, Close: {}, Volume: {} - Live: {}'.format(
                    bt.num2date(data.datetime[0]),
                    data._name,
                    _interval,  # ticker timeframe
                    data.open[0],
                    data.high[0],
                    data.low[0],
                    data.close[0],
                    data.volume[0],
                    _state,
                ))

                # Collect close prices to calculate RSI
                self.rsi_data[ticker].append(data.close[0])
                if len(self.rsi_data[ticker]) >= 20:
                    # Convert to Pandas Series and calculate RSI using 'ta' library
                    close_series = pd.Series(self.rsi_data[ticker])
                    rsi_values = ta.momentum.RSIIndicator(close_series, window=20).rsi()
                    current_rsi = rsi_values.iloc[-1]

                    # Get current MACD values
                    macd_value = self.macd[ticker].macd[0]
                    macd_signal_value = self.macd_signal[ticker][0]
                    macd_hist_value = self.macd[ticker].histo[0]

                    print(f'\t - RSI =', current_rsi)
                    print(f"\t - crossover =", self.crossover[ticker].lines.crossover[0])
                    print(f"\t - MACD = {macd_value}, Signal = {macd_signal_value}, Histogram = {macd_hist_value}")

                    coin_target = self.p.coin_target
                    print(f"\t - Free balance: {self.broker.getcash()} {coin_target}")

                    # signals to open position
                    signal1 = self.crossover[ticker].lines.crossover[0]  # signal 1 - intersection of a fast SMA from bottom to top of a slow SMA
                    signal2 = self.underover_sma[ticker]  # signal 2 - when SMA3 is below SMA2
                    signal3 = (macd_value > macd_signal_value)  # signal 3 - MACD crosses above signal line

                    # signals to close position
                    signal4 = current_rsi < 30  # signal 4 - when the RSI is below 30
                    signal5 = (macd_value < macd_signal_value)  # signal 5 - MACD crosses below signal line

                    if not self.getposition(data):  # If there is no position
                        if signal1 == 1:
                            if signal2 == 1 and signal3:
                                # buy
                                free_money = self.broker.getcash()
                                price = data.close[0]  # by closing price
                                size = (free_money / price) * 0.25  # 25% of available funds
                                print("-" * 50)
                                print(f"\t - buy {ticker} size = {size} at price = {price}")
                                self.orders[data._name] = self.buy(data=data, exectype=bt.Order.Limit, price=price, size=size)
                                print(f"\t - Order has been submitted {self.orders[data._name].p.tradeid} to buy {data._name}")
                                print("-" * 50)

                    else:  # If there is a position
                        if signal4 or signal5:
                            # sell
                            print("-" * 50)
                            print(f"\t - Sell by market {data._name}...")
                            self.orders[data._name] = self.close()  # Request to close a position at the market price
                            print("-" * 50)

    def notify_order(self, order):
        """Changing the status of the order"""
        print("*" * 50)
        order_data_name = order.data._name  # Name of ticker from order
        self.log(f'Order number {order.ref} {order.info["order_number"]} {order.getstatusname()} {"Buy" if order.isbuy() else "Sell"} {order_data_name} {order.size} @ {order.price}')
        if order.status == bt.Order.Completed:  # If the order is fully executed
            if order.isbuy():  # The order to buy
                self.log(f'Buy {order_data_name} @{order.executed.price:.2f}, Price {order.executed.value:.2f}, Commission {order.executed.comm:.2f}')
            else:  # The order to sell
                self.log(f'Sell {order_data_name} @{order.executed.price:.2f}, Price {order.executed.value:.2f}, Commission {order.executed.comm:.2f}')
                self.orders[order_data_name] = None  # Reset the order to enter the position
        print("*" * 50)

    def notify_trade(self, trade):
        """Changing the position status"""
        if trade.isclosed:  # If the position is closed
            self.log(f'Profit on a closed position {trade.getdataname()} Total={trade.pnl:.2f}, No commission={trade.pnlcomm:.2f}')

    def log(self, txt, dt=None):
        """Print string with date to the console"""
        dt = bt.num2date(self.datas[0].datetime[0]) if not dt else dt  # date or date of the current bar
        print(f'{dt.strftime("%d.%m.%Y %H:%M")}, {txt}')  # Print the date and time with the specified text to the console

class MACDStrategy(bt.Strategy):
    """
    Live strategy demonstration with MACD indicators only
    """
    params = (  # Parameters of the trading system
        ('coin_target', ''),
        ('timeframe', ''),
    )

    def __init__(self):
        """Initialization, adding indicators for each ticker"""
        self.orders = {}  # All orders as a dict, for this particularly trading strategy one ticker is one order
        for d in self.datas:  # Running through all the tickers
            self.orders[d._name] = None  # There is no order for ticker yet

        # creating indicators for each ticker
        self.macd = {}
        self.macd_signal = {}
        for i in range(len(self.datas)):
            ticker = list(self.dnames.keys())[i]  # key name is ticker name
            self.macd[ticker] = bt.indicators.MACD(self.datas[i])
            self.macd_signal[ticker] = bt.indicators.MACDHisto(self.datas[i])

    def next(self):
        """Arrival of a new ticker candle"""
        for data in self.datas:  # Running through all the requested bars of all tickers
            ticker = data._name
            status = data._state  # 0 - Live data, 1 - History data, 2 - None
            _interval = self.p.timeframe

            if status in [0, 1]:
                if status: _state = "False - History data"
                else: _state = "True - Live data"

                print('{} / {} [{}] - Open: {}, High: {}, Low: {}, Close: {}, Volume: {} - Live: {}'.format(
                    bt.num2date(data.datetime[0]),
                    data._name,
                    _interval,  # ticker timeframe
                    data.open[0],
                    data.high[0],
                    data.low[0],
                    data.close[0],
                    data.volume[0],
                    _state,
                ))

                # Get current MACD values
                macd_value = self.macd[ticker].macd[0]
                macd_signal_value = self.macd_signal[ticker][0]
                macd_hist_value = self.macd[ticker].histo[0]

                print(f"\t - MACD = {macd_value}, Signal = {macd_signal_value}, Histogram = {macd_hist_value}")

                coin_target = self.p.coin_target
                print(f"\t - Free balance: {self.broker.getcash()} {coin_target}")

                # signals to open position
                signal1 = (macd_value > macd_signal_value)  # signal 1 - MACD crosses above signal line

                # signals to close position
                signal2 = (macd_value < macd_signal_value)  # signal 2 - MACD crosses below signal line

                if not self.getposition(data):  # If there is no position
                    if signal1:
                        # buy
                        free_money = self.broker.getcash()
                        price = data.close[0]  # by closing price
                        size = (free_money / price) * 0.25  # 25% of available funds
                        print("-" * 50)
                        print(f"\t - buy {ticker} size = {size} at price = {price}")
                        self.orders[data._name] = self.buy(data=data, exectype=bt.Order.Limit, price=price, size=size)
                        print(f"\t - Order has been submitted {self.orders[data._name].p.tradeid} to buy {data._name}")
                        print("-" * 50)

                else:  # If there is a position
                    if signal2:
                        # sell
                        print("-" * 50)
                        print(f"\t - Sell by market {data._name}...")
                        self.orders[data._name] = self.close()  # Request to close a position at the market price
                        print("-" * 50)

    def notify_order(self, order):
        """Changing the status of the order"""
        print("*" * 50)
        order_data_name = order.data._name  # Name of ticker from order
        self.log(f'Order number {order.ref} {order.info["order_number"]} {order.getstatusname()} {"Buy" if order.isbuy() else "Sell"} {order_data_name} {order.size} @ {order.price}')
        if order.status == bt.Order.Completed:  # If the order is fully executed
            if order.isbuy():  # The order to buy
                self.log(f'Buy {order_data_name} @{order.executed.price:.2f}, Price {order.executed.value:.2f}, Commission {order.executed.comm:.2f}')
            else:  # The order to sell
                self.log(f'Sell {order_data_name} @{order.executed.price:.2f}, Price {order.executed.value:.2f}, Commission {order.executed.comm:.2f}')
                self.orders[order_data_name] = None  # Reset the order to enter the position
        print("*" * 50)

    def notify_trade(self, trade):
        """Changing the position status"""
        if trade.isclosed:  # If the position is closed
            self.log(f'Profit on a closed position {trade.getdataname()} Total={trade.pnl:.2f}, No commission={trade.pnlcomm:.2f}')

    def log(self, txt, dt=None):
        """Print string with date to the console"""
        dt = bt.num2date(self.datas[0].datetime[0]) if not dt else dt  # date or date of the current bar
        print(f'{dt.strftime("%d.%m.%Y %H:%M")}, {txt}')  # Print the date and time with the specified text to the console
        
class CDCActionZone(bt.Indicator):
    lines = ('signal',)
    params = dict(fast_period=12, slow_period=26, smoothing_period=1)
    plotinfo = dict(plot=True)

    def __init__(self):
        self.addminperiod(max(self.p.fast_period, self.p.slow_period, self.p.smoothing_period))

    def next(self):
        price = pd.Series([self.data.close[i] for i in range(len(self.data))])
        fast_ema = ta.trend.EMAIndicator(price, window=self.p.fast_period).ema_indicator()
        slow_ema = ta.trend.EMAIndicator(price, window=self.p.slow_period).ema_indicator()
        smoothed_price = ta.trend.EMAIndicator(price, window=self.p.smoothing_period).ema_indicator()

        bull = fast_ema > slow_ema
        bear = fast_ema < slow_ema

        green = bull & (smoothed_price > fast_ema)  # Buy
        red = bear & (smoothed_price < fast_ema)    # Sell

        buy_signal = green & ~green.shift(1).fillna(False)
        sell_signal = red & ~red.shift(1).fillna(False)

        if buy_signal.iloc[-1]:
            self.lines.signal[0] = 1  # Buy signal
        elif sell_signal.iloc[-1]:
            self.lines.signal[0] = -1  # Sell signal
        else:
            self.lines.signal[0] = 0  # No signal

class CDCActionZoneStrategy(bt.Strategy):
    params = dict(
        coin_target='',
        timeframe='',
        fast_period=12,
        slow_period=26,
        smoothing_period=1
    )

    def __init__(self):
        self.orders = {d._name: None for d in self.datas}
        self.signal = {d._name: CDCActionZone(d, fast_period=self.p.fast_period, slow_period=self.p.slow_period, smoothing_period=self.p.smoothing_period) for d in self.datas}

    def next(self):
        for data in self.datas:
            ticker = data._name
            status = data._state
            _interval = self.p.timeframe

            if status in [0, 1]:
                if status: _state = "False - History data"
                else: _state = "True - Live data"

                print('{} / {} [{}] - Open: {}, High: {}, Low: {}, Close: {}, Volume: {} - Live: {}'.format(
                    bt.num2date(data.datetime[0]),
                    data._name,
                    _interval,
                    data.open[0],
                    data.high[0],
                    data.low[0],
                    data.close[0],
                    data.volume[0],
                    _state,
                ))

                coin_target = self.p.coin_target
                print(f"\t - Free balance: {self.broker.getcash()} {coin_target}")

                signal = self.signal[ticker].lines.signal[0]

                if not self.getposition(data):
                    if signal == 1:
                        free_money = self.broker.getcash()
                        price = data.close[0]
                        size = (free_money / price) * 0.25  # 25% of available funds
                        print("-" * 50)
                        print(f"\t - buy {ticker} size = {size} at price = {price}")
                        self.orders[data._name] = self.buy(data=data, exectype=bt.Order.Limit, price=price, size=size)
                        print(f"\t - Order has been submitted {self.orders[data._name].p.tradeid} to buy {data._name}")
                        print("-" * 50)
                else:
                    if signal == -1:
                        print("-" * 50)
                        print(f"\t - Sell by market {data._name}...")
                        self.orders[data._name] = self.close()
                        print("-" * 50)

    def notify_order(self, order):
        print("*" * 50)
        order_data_name = order.data._name
        self.log(f'Order number {order.ref} {order.info["order_number"]} {order.getstatusname()} {"Buy" if order.isbuy() else "Sell"} {order_data_name} {order.size} @ {order.price}')
        if order.status == bt.Order.Completed:
            if order.isbuy():
                self.log(f'Buy {order_data_name} @{order.executed.price:.2f}, Price {order.executed.value:.2f}, Commission {order.executed.comm:.2f}')
            else:
                self.log(f'Sell {order_data_name} @{order.executed.price:.2f}, Price {order.executed.value:.2f}, Commission {order.executed.comm:.2f}')
                self.orders[order_data_name] = None
        print("*" * 50)

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'Profit on a closed position {trade.getdataname()} Total={trade.pnl:.2f}, No commission={trade.pnlcomm:.2f}')

    def log(self, txt, dt=None):
        dt = bt.num2date(self.datas[0].datetime[0]) if not dt else dt
        print(f'{dt.strftime("%d.%m.%Y %H:%M")}, {txt}')