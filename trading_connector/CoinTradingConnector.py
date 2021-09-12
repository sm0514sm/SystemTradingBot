from trading_connector.AbstractTradingConnector import AbstractTradingConnector
from util.MethodLoggerDecorator import MethodLoggerDecorator


class CoinTradingConnector(AbstractTradingConnector):
    @MethodLoggerDecorator
    def ready_trading(self):
        pass

    @MethodLoggerDecorator
    def buy(self, name, price_amount):
        pass

    @MethodLoggerDecorator
    def sell(self, name, count_amount):
        pass

    @MethodLoggerDecorator
    def get_current_price(self, name):
        pass

    @MethodLoggerDecorator
    def get_current_prices(self, names):
        pass

    @MethodLoggerDecorator
    def get_min_max(self, names):
        pass

    @MethodLoggerDecorator
    def get_balance(self, name="KRW"):
        pass

    @MethodLoggerDecorator
    def get_avg_buy_price(self, name):
        pass
