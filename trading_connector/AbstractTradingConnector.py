import logging
from abc import *


class AbstractTradingConnector(metaclass=ABCMeta):
    logger = logging.getLogger("SystemLogger")
    # coin_logger = logging.getLogger("CoinInfoLogger")

    def __init__(self):
        self.hold_krw = None
        self.cmm_config = None
        self.discord_conn = None
        self.heartbeat_interval = None
        self.logger.debug(type(self).__name__)
        self.last_hb_time = None
        self.last_report_time = None

    @abstractmethod
    def ready_trading(self):
        """ Connector의 거래를 위한 준비 """
        pass

    @abstractmethod
    def buy(self, name, price_amount) -> bool:
        """ price_amount원 만큼 시장가 매수

        Args:
            name: 매수할 종목명
            price_amount: 매수할 양(KRW)
        Returns:
            True 매수 성공, False 매수 실패
        """
        pass

    @abstractmethod
    def sell(self, name, count_amount, status):
        """ name 종목 모두 시장가 매도

        Args:
            name: 매도할 종목명
            count_amount: 매도할 개수
            status:
        """
        pass

    @abstractmethod
    def update_current_infos(self, stocks) -> None:
        """ stocks의 현재가, 거래량 세팅 """
        pass

    @abstractmethod
    def update_last_infos(self, stocks) -> None:
        """ stocks의 전일 거래량 세팅"""
        pass

    @abstractmethod
    def apply_pickles(self, stock_list: list, strategy_name: str) -> list:
        """ pickles로 저장한 데이터를 불러옴 """
        pass

    @abstractmethod
    def save_pickles(self, stock_list: list, strategy_name: str) -> None:
        """ 주식 데이터를 pickles로 저장함 """
        pass

    @abstractmethod
    def set_min_max(self, names) -> dict:
        """ names 종목들의 기간중 최소최대 가격 조회 """
        pass

    @abstractmethod
    def set_min_max_one(self, name) -> dict:
        """ nams 종목의 기간중 최소최대 가격 조회 """
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

    @abstractmethod
    def heartbeat(self):
        pass

    @abstractmethod
    def daily_report(self):
        pass
