from enum import IntEnum, unique, auto
from datetime import datetime

from util.Calculator import calculate_rate


class Status(IntEnum):
    PASS = auto()  # 한번 매도 했던 코인은 다음번까지 매수하지 않음
    WAIT = auto()
    TRY_BUY = auto()  # 매수 예약 상태
    TRY_SELL = auto()  # 매수 예약 상태
    BOUGHT = auto()  # 1개라도 산 경우
    END_BUY = auto()  # MAX_DCA_BUY_CNT번 매수를 한 경우
    SELL_READY = auto()  # 매도 준비 (매도 완료 후 PASS 상태)
    WARN = -1  # 유의종목
    NEW = -2  # 상장한지 얼마되지 않은 종목


class CmmInfo:
    def __init__(self, *args, **kwargs) -> None:
        self.min: float = 0 if not args else args[0]  # N_DAYS 중 최저가
        self.max: float = 0 if not args else args[1]  # N_DAYS 중 최고가

        # 주문 전 정보
        self.tg_buy_price: float = 0  # 목표 매수 평균가 (최저점 돌파시 설정됨)
        self.tg_sell_price: float = 0  # 목표 매도 평균가 (최고점 돌파시 설정됨)


class SvbInfo:
    def __init__(self, *args) -> None:
        self.min: float = 0 if not args else args[0]  # 전날 최저가
        self.max: float = 0 if not args else args[1]  # 전날 최고가

        # 주문 전 정보
        self.tg_buy_price: float = 0  # 목표 매수 평균가
        self.tg_sell_price: float = 0  # 목표 매도 평균가 (매수시 설정됨)


class MscInfo:
    def __init__(self) -> None:
        self.MCS_bought_cnt: int = 0  # MCS 전략 기법에서 매수한 횟수
        self.MCS_buy_price: list = [0, 0, 0, 0, 0]  # MCS 전략 기법에서 매수 목표 금액들


class Coin:
    # price는 코인의 가격, amount는 원화가
    # amount = price * volume
    def __init__(self, coin_name: str, check_time: str = "", **kwargs):
        self.name: str = coin_name
        self.check_time: str = check_time
        self.status: IntEnum = Status.WAIT
        self.low_price: float = 0  # 금일 저가
        self.high_price: float = 0  # 금일 고가
        self.open_price: float = 0  # 금일 시가
        self.current_price: float = 0  # 현재 가격
        self.current_volume: float = 0  # 현재 거래량
        self.last_volume: float = 0  # 전일 거래량

        self.buy_uuid: str = ""
        self.sell_uuid: str = ""

        self.variability: float = 0

        self.dca_buy_cnt: int = 0  # 분할매수한 개수
        self.target_buy_price: float = 0  # 목표 매수 금액
        self.target_profit_cut_sell_price: float = 0  # 익절 목표 매수 금액
        self.target_loss_cut_sell_price: float = 0  # 손절 목표 매수 금액
        self.buy_volume_cnt: int = 0  # 구매한 개수
        self.bought_amount: float = 0  # 구매한 가격 (양)
        self.avg_buy_price: float = 0  # 구매한 코인 평균가격
        self.avg_sell_price: float = 0  # 매도한 코인 평균가격
        self.sold_amount: float = 0  # 매도한 가격 (양)

        self.earnings_ratio: float = 0  # 현재 코인 수익률
        self.max_earnings_ratio: float = 0  # 현재 봉에서 최대 수익률

        self.cmm_info = CmmInfo()
        self.msc_info = MscInfo()
        self.svb_info = SvbInfo()

    def set_cmm_info(self, minimum, maximum):
        self.cmm_info.min = minimum
        self.cmm_info.max = maximum

    def get_next_buy_amount(self, start_amount: int | float, multiple_amount: int | float):
        """ 다음 매수 시도할 금액을 반환 """
        return start_amount + multiple_amount * self.dca_buy_cnt

    def __repr__(self) -> str:
        return f'Coin({self.name:>6}, ' \
               f'{self.status.name:>10}, ' \
               f'현재가: {int(self.current_price) if self.current_price > 1 else round(self.current_price):>8}, ' \
               f'목표가: {int(self.target_buy_price) if self.target_buy_price > 1 else round(self.target_buy_price):>8}' \
               f'({round(calculate_rate(self.target_buy_price, self.current_price), 1):>5}), ' \
               f'volume: {round(self.buy_volume_cnt, 2):>10}, ' \
               f'avg_price: {round(self.avg_buy_price, 1):8.1f}), ' \
               f'분할매수횟수: {self.dca_buy_cnt:2}'


if __name__ == "__main__":
    pass
    # print(buy_stock(f'KRW-ETH', price=10000, sleep=3))
