import logging
from abc import *
from datetime import date

from object.Coin import Coin
from trading_connector.AbstractTradingConnector import AbstractTradingConnector


class AbstractStrategy(metaclass=ABCMeta):
    connector: AbstractTradingConnector
    logger = logging.getLogger("SystemLogger")
    coin_logger = logging.getLogger("CoinInfoLogger")
    stocks_name = list[str]
    stocks_list = list[Coin]
    last_date = None

    def __init__(self, trading_connector: AbstractTradingConnector):
        self.logger.debug(type(self).__name__)
        self.connector = trading_connector
        trading_connector.ready_trading()

        stocks_name = self.connector.get_watching_list()
        self.stocks_list = self.connector.make_obj_list(stocks_name)

    @abstractmethod
    def run_strategy(self):
        pass
