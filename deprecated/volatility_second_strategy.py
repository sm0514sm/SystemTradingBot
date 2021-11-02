import os
from object.Coin import Coin, Status
from function.get_candles import get_candles
from function.get_now_time import get_now_time
from function.order_stock import *
from function.print_your_config import print_order_config
from function.get_market_code import get_market_code
from function.get_account import *

config = configparser.ConfigParser()
config.read('config.ini', encoding='UTF8')

VM_order_config = config['VB_ORDER']

CANDLE_TYPE: str = VM_order_config.get('CANDLE_TYPE')
UNIT: int = VM_order_config.getint('MINUTE_CANDLE_UNIT')

PERCENT_BUY_RANGE: int = VM_order_config.getint('PERCENT_OF_BUY_RANGE')
PERCENT_OF_STOP_LOSS: float = VM_order_config.getfloat('PERCENT_OF_STOP_LOSS')

COIN_DIV_CNT: int = VM_order_config.getint('COIN_DIV_CNT')
COIN_DIV_SELECT: int = VM_order_config.getint('COIN_DIV_SELECT')
COIN_MAXIMUM: int = VM_order_config.getint('COIN_MAXIMUM')


def volatility_strategy(coins_name: list):
    os.makedirs('logs', exist_ok=True)
    print(f'{get_now_time()} 시작가: {get_krw():.2f}')

    print_order_config(config.items(section="VB_ORDER"))
    coin_dict = dict()
    for coin_name in coins_name:
        coin_dict[coin_name] = Coin(coin_name)
    while True:
        for i, coin in enumerate(coin_dict.values()):
            candles = get_candles('KRW-' + coin.name, count=2, minute=UNIT, candle_type=CANDLE_TYPE)
            coin.high_price = max(candles[0]["trade_price"], coin.high_price)
            now = candles[0]['candle_date_time_kst']

            if coin.status == Status.BOUGHT:
                coin.earnings_ratio = (candles[0]["trade_price"] - coin.avg_buy_price) / candles[0]["trade_price"] * 100
                coin.max_earnings_ratio = max(coin.earnings_ratio, coin.max_earnings_ratio)
            if coin.status == Status.WAIT:
                print(f'{get_now_time()} {coin.name:>6}({set_state_color(coin.status)})| '
                      f'목표 가: {coin.buy_price:>11.2f}, 현재 가: {candles[0]["trade_price"]:>10}'
                      f' ({set_dif_color(candles[0]["trade_price"], coin.buy_price)}) '
                      f'최대 {coin.max_earnings_ratio:>6.2f} %')
            elif coin.status == Status.BOUGHT:
                print(f'{get_now_time()} {coin.name:>6}({set_state_color(coin.status)})| '
                      f'구매 가: {coin.avg_buy_price:>11.2f}, 현재 가: {candles[0]["trade_price"]:>10}'
                      f' ({set_dif_color(candles[0]["trade_price"], coin.avg_buy_price)}) '
                      f'최대 {coin.max_earnings_ratio:6.2f} %')

            # 매도 조건
            # 1. 시간 캔들이 바뀐 경우
            # 2. 수익률이 5 % 이상인 경우
            if coin.check_time != now or (coin.status == Status.BOUGHT and coin.earnings_ratio >= 5)\
                    or (coin.status == Status.BOUGHT and coin.earnings_ratio <= -5):
                print(f'1. time_change: {coin.check_time != now} '
                      f'2. ratio: {coin.earnings_ratio}')
                if coin.check_time != now and i == 0:
                    print(f'----------------------------------- UPDATE ---------------------------------------')
                if coin.status == Status.BOUGHT:
                    sell_result = coin.sell_coin()
                    print(
                        f'\033[104m{get_now_time()} {coin.name:>6}(  SELL)| {int(round(get_sell_price(sell_result)))}원\033[0m')
                if coin.check_time != now:
                    coin.status = Status.WAIT
                    coin.max_earnings_ratio = 0
                    coin.earnings_ratio = 0
                if coin.check_time != now and i == len(coin_dict) - 1:
                    print(f'---------------------------------------------------------------------------------')
                coin.check_time = now
                coin.variability = candles[1]['high_price'] - candles[1]['low_price']
                coin.buy_price = candles[0]["opening_price"] + coin.variability * (PERCENT_BUY_RANGE / 100)
                coin.high_price = candles[0]["opening_price"]
                coin.buy_balance = cal_buy_balance(coin.variability, coin.high_price)
                if coin.buy_balance == 0:
                    coin.status = Status.PASS
                print(f'{coin.name}| variability:{coin.variability}, buy_price:{coin.buy_price}, buy_balance:{coin.buy_balance}')
            else:  # 시간이 동일하다면
                if coin.status != Status.WAIT:
                    continue
                if coin.variability == 0 or candles[0]['trade_price'] <= coin.buy_price:
                    continue

                # 매수
                buy_result = coin.buy_coin(price=coin.buy_balance)
                if not buy_result:
                    continue
                print(f'\033[101m{get_now_time()} {coin.name:>6}(   BUY)| {coin.bought_amount}원\033[0m')


def cal_buy_balance(variability, base_price) -> int:
    # 0.01 ~ 0.2
    base = min(variability / base_price * 1.25, 0.4)
    if base <= 0.03:
        return 0
    return base * 100 * 10000


# 최대 수익률 대비 몇 % 떨어지면 팔지 계산
def max_drop_rule(max_earnings_ratio):
    if max_earnings_ratio < 3:
        return PERCENT_OF_STOP_LOSS
    return max_earnings_ratio - max_earnings_ratio // 2.5


def set_state_color(state) -> str:
    if state == Status.BOUGHT:
        return f'\033[91m{state.name:>6}\033[0m'
    elif state == Status.ADDBUY:
        return f'\033[96m{state.name:>6}\033[0m'
    else:
        return f'{state.name:>6}'


def set_dif_color(a, b) -> str:
    value = (a - b) / a * 100
    if value < 0:
        return f'\033[34m{value:>6.2f}%\033[0m'
    else:
        return f'\033[31m{value:>6.2f}%\033[0m'


if __name__ == '__main__':
    volatility_strategy(get_market_code(div_cnt=COIN_DIV_CNT, maximum=COIN_MAXIMUM)[COIN_DIV_SELECT])
