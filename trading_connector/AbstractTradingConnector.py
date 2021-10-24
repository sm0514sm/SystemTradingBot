import logging
from abc import *


class AbstractTradingConnector(metaclass=ABCMeta):
    logger = logging.getLogger("SystemLogger")

    def __init__(self):
        self.logger.debug(type(self).__name__)

    @abstractmethod
    def ready_trading(self):
        """ Connector의 거래를 위한 준비 """
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
    def get_current_price(self, name) -> float:
        """ name 종목의 현재가를 반환 """
        pass

    @abstractmethod
    def set_current_prices(self, names) -> None:
        """ name 종목들의 현재가를 세팅 """
        pass

    @abstractmethod
    def set_min_max(self, names) -> dict:
        """ names 종목들의 기간중 최소최대 가격 조회 """
        pass

    @abstractmethod
    def get_balance(self, name="KRW") -> float:
        """ 현재 가지고 있는 종목 수량 조회 (기본값 KRW) """
        pass

    @abstractmethod
    def get_balances(self):
        """ 현재 가지고 있는 모든 종목 조회 """
        pass

    @abstractmethod
    def get_avg_buy_price(self, name) -> float:
        """ 현재 가지고 있는 종목의 평균 매수가 조회 """
        pass

    @abstractmethod
    def get_watching_list(self) -> list:
        """ 전략에 적용할 종목 리스트 조회 """
        pass

    @abstractmethod
    def make_obj_list(self, names) -> list:
        """ 전략에 적용할 종목 객체 리스트 생성 """
        pass

    @abstractmethod
    def add_bought_stock_info(self, stock_list):
        """ 이미 가지고 있는 종목들 정보 추가 """
        pass

    @abstractmethod
    def check_config(self):
        """ 설정 파일 유효성 검사 """
        pass
