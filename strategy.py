import backtrader as bt
import logging
from indicators.combined.combined_trading_signal import combined_trading_signal

class CombinedStrategy(bt.Strategy):
    params = (  # Parameters of the trading system
        ('coin_target', ''),
        ('timeframe', ''),
    )

    def __init__(self):
        self.orders = {}
        for d in self.datas:
            self.orders[d._name] = None  # There is no order for ticker yet

        # Setup logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def next(self):
        for data in self.datas:
            ticker = data._name
            status = data._state
            _interval = self.p.timeframe

            if status in [0, 1]:
                if status:
                    _state = "False - History data"
                else:
                    _state = "True - Live data"

                self.logger.info('{} / {} [{}] - Open: {}, High: {}, Low: {}, Close: {}, Volume: {} - Live: {}'.format(
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

                kl = {
                    'Open': data.open[0],
                    'High': data.high[0],
                    'Low': data.low[0],
                    'Close': data.close[0],
                    'Volume': data.volume[0]
                }

                final_signal = combined_trading_signal(kl)

                if not self.getposition(data):
                    if final_signal == 'up':
                        free_money = self.broker.getcash()
                        price = data.close[0]
                        size = (free_money / price) * 0.25  # 25% of available funds
                        self.logger.info("-" * 50)
                        self.logger.info(f"\t - Buy {ticker} size = {size} at price = {price}")
                        self.orders[data._name] = self.buy(data=data, exectype=bt.Order.Market, size=size)
                        self.logger.info(f"\t - Order has been submitted to buy {data._name}")
                        self.logger.info("-" * 50)
                else:
                    if final_signal == 'down':
                        self.logger.info("-" * 50)
                        self.logger.info(f"\t - Sell {ticker}...")
                        self.orders[data._name] = self.close(data=data)
                        self.logger.info("-" * 50)

    def notify_order(self, order):
        self.logger.info("*" * 50)
        order_data_name = order.data._name
        self.log(f'Order {order.ref} {order.info["order_number"]} {order.getstatusname()} {"Buy" if order.isbuy() else "Sell"} {order_data_name} {order.size} @ {order.price}')
        if order.status == bt.Order.Completed:
            if order.isbuy():
                self.log(f'Buy {order_data_name} @{order.executed.price:.2f}, Price {order.executed.value:.2f}, Commission {order.executed.comm:.2f}')
            else:
                self.log(f'Sell {order_data_name} @{order.executed.price:.2f}, Price {order.executed.value:.2f}, Commission {order.executed.comm:.2f}')
                self.orders[order_data_name] = None
        self.logger.info("*" * 50)

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'Profit on a closed position {trade.getdataname()} Total={trade.pnl:.2f}, No commission={trade.pnlcomm:.2f}')

    def log(self, txt, dt=None):
        dt = bt.num2date(self.datas[0].datetime[0]) if not dt else dt
        self.logger.info(f'{dt.strftime("%d.%m.%Y %H:%M")}, {txt}')
