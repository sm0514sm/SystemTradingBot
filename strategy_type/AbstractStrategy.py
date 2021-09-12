import logging
from abc import *

from trading_connector.AbstractTradingConnector import AbstractTradingConnector


class AbstractStrategy(metaclass=ABCMeta):
    connector: AbstractTradingConnector
    logger = logging.getLogger("SystemLogger")

    def __init__(self, trading_connector: AbstractTradingConnector):
        self.logger.debug(type(self).__name__)
        self.connector = trading_connector
        trading_connector.ready_trading()

    @abstractmethod
    def run_strategy(self):
        pass
