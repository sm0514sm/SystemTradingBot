from enum import IntEnum
from datetime import datetime


class Status(IntEnum):
    PASS = 0  # 한번 매도 했던 코인은 다음번까지 매수하지 않음
    WAIT = 1
    BOUGHT = 2
    TRYBUY = 3
    ADDBUY = 4
    WARN = -1  # 유의종목


class CmmInfo:
    def __init__(self, *args, **kwargs) -> None:
        self.min: float = 0 if not args else args[0]  # N_DAYS 중 최저가
        self.max: float = 0 if not args else args[1]  # N_DAYS 중 최고가

        # 주문 전 정보
        self.tg_buy_price: float = 0  # 목표 매수 평균가 (최저점 돌파시 설정됨)
        self.tg_sell_price: float = 0  # 목표 매도 평균가 (최고점 돌파시 설정됨)


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
        self.balance: float = 0
        self.status: IntEnum = Status.WAIT
        self.current_price: float = 0

        self.variability: float = 0

        self.buy_price: float = 0  # 목표 매수 금액
        self.buy_volume: int = 0  # 구매한 개수
        self.bought_amount: float = 0  # 구매한 가격 (양)
        self.avg_buy_price: float = 0  # 구매한 코인 평균가격
        self.buy_time: datetime = datetime(2021, 1, 1)  # 구매한 시점

        self.high_price: float = 0
        self.earnings_ratio: float = 0  # 현재 코인 수익률
        self.max_earnings_ratio: float = 0  # 현재 봉에서 최대 수익률

        self.cmm_info = CmmInfo()
        self.msc_info = MscInfo()

    def set_cmm_info(self, minimum, maximum):
        self.cmm_info.min = minimum
        self.cmm_info.max = maximum

    def __repr__(self) -> str:
        return f'Coin({self.name:>6},{self.status.name:>6},{int(self.current_price):>8})'
    # 매수 개수 확인
    # def update_balance(self):
    #     for _ in range(10):
    #         time.sleep(0.5)
    #         for account in get_account():
    #             if account.get('currency') == self.name:
    #                 self.balance = account.get('balance')
    #                 self.avg_buy_price = float(account.get('avg_buy_price'))
    #                 break
    #         if self.balance:
    #             break
    #
    # def buy_coin(self, price, limit=False, addbuy=False):
    #     if limit:
    #         buy_result = buy_stock(f'KRW-{self.name}',
    #                                price=self.buy_price, volume=price / self.buy_price, ord_type="limit")
    #         self.status = Status.TRYBUY
    #     else:
    #         buy_result = buy_stock(f'KRW-{self.name}', price=price)
    #         self.status = Status.ADDBUY if addbuy else Status.BOUGHT
    #     if buy_result.get('error'):
    #         self.status = Status.PASS
    #         return ""
    #     self.buy_time = datetime.now()
    #     self.uuid = buy_result.get('uuid')
    #     self.bought_amount = buy_result.get('locked')
    #     self.update_balance()
    #     return buy_result
    #
    # def sell_coin(self):
    #     self.update_balance()
    #     sell_result = sell_stock(f'KRW-{self.name}', self.balance)
    #     self.status = Status.PASS
    #     return sell_result.get('uuid')
    #
    # def cansel_buy(self):
    #     pass


if __name__ == "__main__":
    pass
    # print(buy_stock(f'KRW-ETH', price=10000, sleep=3))
