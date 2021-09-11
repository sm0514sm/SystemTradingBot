import logging
from abc import *


class AbstractTradingConnector(metaclass=ABCMeta):
    logger = logging.getLogger("SystemLogger")

    def __init__(self):
        self.logger.debug(type(self).__name__)

    @abstractmethod
    def ready_trading(self):
        """ Connector의 거래를 위한 준비를 함
        코인: settings 불러오기
        주식: settings 불러오기 + cybosPlus
        """
        pass

    @abstractmethod
    def buy(self, name, price_amount):
        """ price_amount원 만큼 시장가 매수
        Args:
            name: 매수할 종목명
            price_amount: 매수할 양(KRW)
        """
        pass

    @abstractmethod
    def sell(self, name, count_amount):
        """ name 종목 모두 시장가 매도
        Args:
            name: 매도할 종목명
            count_amount: 매도할 개수
        """
        pass

    @abstractmethod
    def get_current_price(self, name):
        """ name 종목의 현재가를 반환
        Args:
            name: 조회할 종목명
        """
        pass

    def __getattribute__(self, name):
        if callable(object.__getattribute__(self, name)) and not name.startswith('__'):
            self.logger.debug(f"{type(self).__name__}.{name}")
        return object.__getattribute__(self, name)
