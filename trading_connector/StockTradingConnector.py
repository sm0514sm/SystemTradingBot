from trading_connector.AbstractTradingConnector import AbstractTradingConnector
from util.MethodLoggerDecorator import MethodLoggerDecorator


class StockTradingConnector(AbstractTradingConnector):
    @MethodLoggerDecorator
    def ready_trading(self):
        pass

    @MethodLoggerDecorator
    def buy(self, a, b):
        pass

    @MethodLoggerDecorator
    def sell(self, name, count_amount):
        pass

    @MethodLoggerDecorator
    def get_current_price(self, name):
        pass