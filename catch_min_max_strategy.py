"""
최근 COUNT 붕 중에서 현재가가 최저가의 VALUE_K % 이상 오르면 매수,
최고가의 VALUE_K % 이상 내려가면 매도하는 전략
"""
# 각 코인들의 COUNT 붕에서 최고가와 최저가를 가져옴
# if 날이 변하면:
#   각 코인들의 COUNT 붕 최고가 최저가 갱신
# if 상태 = WAIT and 현재가 < 최저가:
#   현재가를 최저가
#   상태 = BUY_READY
# if BUY_READY and 현재가 > 최저가 * (1 + VALUE_K)면
#   매수
#   상태 = BOUGHT
# if 상태 = BOUGHT and 현재가 > 최고가:
#   현재가 = 최고가
#   상태 = SELL_READY
# if SELL_READY and 현재가 < 최고가 * (1 - VALUE_K)면
#   매도
#   상태 = WAIT

# 도지코인 예시
# price: 624 (원)
# volume: 10 (개)
# amount: 6240 (원)
import configparser
from enum import Enum

from function.get_now_time import get_now_time
from pyupbit import *

config = configparser.ConfigParser()
config.read('config.ini', encoding='UTF8')

config = config['UPBIT']
access = config.get("UPBIT_OPEN_API_ACCESS_KEY")
secret = config.get("UPBIT_OPEN_API_SECRET_KEY")
upbit = Upbit(access, secret)

CMMS_config = configparser.ConfigParser()
CMMS_config.read('CMMS_config.ini', encoding='UTF8')

CMMS_config = CMMS_config['CONFIG']
COUNT = CMMS_config.getint('COUNT')
INTERVAL = CMMS_config.get('INTERVAL')
VALUE_K = CMMS_config.getfloat('VALUE_K')
DELAY = CMMS_config.getfloat('DELAY')
BUY_AMOUNT = CMMS_config.getint('BUY_AMOUNT')
PROFIT_RATE = CMMS_config.getint('PROFIT_RATE')


# 코인에 대한 상태 정보
class Status(Enum):
    WAIT = 0
    BUY_READY = 1
    BOUGHT = 2
    SELL_READY = 3


class Coin(object):
    def __init__(self, *args, **kwargs):
        self.min: float = 0 if not args else args[0]  # N_DAYS 중 최저가
        self.max: float = 0 if not args else args[1]  # N_DAYS 중 최고가
        self.status: Status = Status.WAIT  # 현재 상태
        self.last_time: datetime = None

        # 주문 정보
        self.avg_buy_price: float = 0  # 매수 평균가
        self.avg_sell_price: float = 0  # 매도 평균가
        self.buy_volume: float = 0  # 매수 거래량
        self.sell_volume: float = 0  # 매도 거래량

        # 주문 전 정보
        self.target_buy_price: float = 0  # 목표 매수 평균가 (최저점 돌파시 설정됨)
        self.target_sell_price: float = 0  # 목표 매도 평균가 (최고점 돌파시 설정됨)

    def __str__(self):
        return f'{{min:{self.min}, max:{self.max}, status:{self.status.name}, avg_buy_price:{self.avg_buy_price},' \
               f'avg_sell_price:{self.avg_sell_price}, buy_volume:{self.buy_volume}, sell_volume:{self.sell_volume}}}'


# 코인의 정보(최소값, 최대값)을 가져옴
def get_coin_min_max(coins_name, cnt) -> dict:
    print("get_coin_min_max")
    coin_dict = dict()
    for coin_name in coins_name:
        ohlcv = get_ohlcv(coin_name, interval=INTERVAL, count=cnt)
        coin_dict[coin_name] = Coin(min(ohlcv['low']), max(ohlcv['high']), max(ohlcv.index))
    return coin_dict


# 코인의 정보(최소값, 최대값)을 업데이트 함
def reset_min_max(coin_dict: dict, cnt) -> None:
    print("reset_min_max")
    for coin in coin_dict.keys():
        ohlcv = get_ohlcv(coin, interval=INTERVAL, count=cnt)
        coin_dict[coin].min = min(ohlcv['low'])
        coin_dict[coin].max = max(ohlcv['high'])


# 얼마나 자주 전체 코인에 대한 정보를 업데이트할 것인지 결정
def calculate_reset_cnt() -> int:
    cnt = 0
    if INTERVAL == "day":
        cnt = 86400 / DELAY
    elif INTERVAL == "minute1":
        cnt = 60 * 1 / DELAY
    elif INTERVAL == "minute3":
        cnt = 60 * 3 / DELAY
    elif INTERVAL == "minute5":
        cnt = 60 * 5 / DELAY
    elif INTERVAL == "minute10":
        cnt = 60 * 10 / DELAY
    elif INTERVAL == "minute15":
        cnt = 60 * 15 / DELAY
    elif INTERVAL == "minute30":
        cnt = 60 * 30 / DELAY
    elif INTERVAL == "minute60":
        cnt = 60 * 60 / DELAY
    elif INTERVAL == "minute240":
        cnt = 60 * 240 / DELAY
    return min(1200, cnt)


# 구매한 코인 정보를 가져와 업데이트
def add_bought_coin_info(coin_dict: dict) -> None:
    coins_info = upbit.get_balances()
    for coin_info in coins_info:
        if coin_info['currency'] == 'KRW':
            continue
        try:
            coin: Coin = coin_dict['KRW-' + coin_info['currency']]
            coin.status = Status.BOUGHT
            coin.avg_buy_price = float(coin_info['avg_buy_price'])
            coin.buy_volume = float(coin_info['balance'])
        except KeyError:
            pass


def calculate_rate(target, base) -> float:
    return (target - base) / base


def catch_min_max_strategy(coins_name: list):
    # {'coin_name': {min: 0, max: 0, status: 0}, ...}
    coin_dict = get_coin_min_max(coins_name, cnt=COUNT)
    add_bought_coin_info(coin_dict)
    cnt = 0
    reset_cnt = calculate_reset_cnt()
    while True:
        cnt += 1
        if cnt > reset_cnt:
            reset_min_max(coin_dict, cnt=COUNT)
            cnt = 0
        print(f"\n{get_now_time()} |{'COIN':-^10}|-{'MIN':-^10}|{'MAX':-^10}|{'STATUS':-^10}|{'CURRENT':-^10}|", end="")
        time.sleep(DELAY)
        for coin, current_price in get_current_prices(coins_name):
            print(f"\n{get_now_time()}  {coin:10}: {coin_dict[coin].min:10} {coin_dict[coin].max:10} "
                  f"{coin_dict[coin].status.name:^10} {current_price:10}", end=" ")

            if coin_dict[coin].status == Status.WAIT and current_price < coin_dict[coin].min \
                    and upbit.get_balance() >= BUY_AMOUNT:
                coin_dict[coin].status = Status.BUY_READY
            elif coin_dict[coin].status == Status.BUY_READY:
                coin_dict[coin].min = min(coin_dict[coin].min, current_price)
                coin_dict[coin].target_buy_price = coin_dict[coin].min * (1 + VALUE_K)
                print(f"{coin_dict[coin].target_buy_price:.1f}", end=" ")
                if current_price > coin_dict[coin].target_buy_price:
                    print(upbit.buy_market_order(coin, BUY_AMOUNT))
                    time.sleep(1)
                    coin_dict[coin].status = Status.BOUGHT
                    coin_dict[coin].avg_buy_price = float(upbit.get_avg_buy_price(coin[4:]))
                    print("avg_buy_price2: ", coin_dict[coin].avg_buy_price)
            elif coin_dict[coin].status == Status.BOUGHT \
                and (current_price > coin_dict[coin].max
                     or calculate_rate(current_price, coin_dict[coin].avg_buy_price) >= PROFIT_RATE):
                coin_dict[coin].status = Status.SELL_READY
            elif coin_dict[coin].status == Status.SELL_READY:
                coin_dict[coin].max = max(coin_dict[coin].max, current_price)
                coin_dict[coin].target_sell_price = coin_dict[coin].max * (1 - VALUE_K)
                print(f"{coin_dict[coin].target_sell_price:.1f}", end=" ")
                if current_price < coin_dict[coin].target_sell_price\
                        or calculate_rate(current_price, coin_dict[coin].avg_buy_price) >= PROFIT_RATE:
                    print(upbit.sell_market_order(coin, upbit.get_balance(coin[4:])))
                    coin_dict[coin].status = Status.WAIT
                    coin_dict[coin].avg_sell_price = current_price
                    print(f"{coin_dict[coin].avg_buy_price} -> {coin_dict[coin].avg_sell_price}"
                          f"({(coin_dict[coin].avg_sell_price - coin_dict[coin].avg_buy_price) / coin_dict[coin].avg_buy_price})")
                    coin_dict[coin] = Coin(coin_dict[coin].min, coin_dict[coin].max)  # 초기화
            else:
                pass


def get_current_prices(coins_name):
    if len(coins_name) >= 100:
        result1: dict = get_current_price(coins_name[:100])
        result2: dict = get_current_price(coins_name[100:])
        result1.update(result2)
        return result1.items()
    else:
        return get_current_prices(coins_name)


if __name__ == "__main__":
    # catch_min_max_strategy(["KRW-BTC", "KRW-ETC", "KRW-ETH", "KRW-DOGE"])
    # catch_min_max_strategy(["KRW-FCT2"])
    catch_min_max_strategy(get_tickers(fiat="KRW"))
