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

MCS_order_config = config['MCS_ORDER']
CANDLE_TYPE: str = MCS_order_config.get('CANDLE_TYPE')
UNIT: int = MCS_order_config.getint('MINUTE_CANDLE_UNIT')

COIN_DIV_CNT: int = MCS_order_config.getint('COIN_DIV_CNT')
COIN_DIV_SELECT: int = MCS_order_config.getint('COIN_DIV_SELECT')
COIN_MAXIMUM: int = MCS_order_config.getint('COIN_MAXIMUM')

MAX_BOUGHT_CNT: int = MCS_order_config.getint('MAXIMUM_BOUGHT_CNT')
BUY_DIF_RANGE: float = MCS_order_config.getfloat('BUY_DIF_RANGE')
BUY_AMOUNT: int = MCS_order_config.getint('BUY_AMOUNT')


def min_catch_strategy(coins_name: list):
    os.makedirs('logs', exist_ok=True)
    log_file = open("logs/MCS_order.log", "a")
    print(f'{get_now_time()} 시작가: {get_krw():.2f}')
    log_file.write(f'{get_now_time()} 시작가: {get_krw():.2f}\n')

    print_order_config(config.items(section="VB_ORDER"))
    coin_dict = dict()
    for coin_name in coins_name:
        coin_dict[coin_name] = Coin(coin_name)
    while True:
        for i, coin in enumerate(coin_dict.values()):
            try:
                candles = get_candles('KRW-' + coin.name, count=2, minute=UNIT, candle_type=CANDLE_TYPE)
                coin.high_price = max(candles[0]["trade_price"], coin.high_price)
                now = candles[0]['candle_date_time_kst']

                if coin.status != Status.PASS:
                    print(f'{get_now_time()} {coin.name:>6}({set_state_color(coin.status)}{coin.MCS_bought_cnt})| '
                          f'목표 가: {coin.MCS_buy_price[coin.MCS_bought_cnt] if coin.MCS_bought_cnt < MAX_BOUGHT_CNT else 0:>11.2f}, '
                          f'현재 가: {candles[0]["trade_price"]:>10},'
                          f'구매 가: {coin.avg_buy_price:>11.2f}'
                          f' ({set_dif_color(candles[0]["trade_price"], coin.MCS_buy_price[coin.MCS_bought_cnt] if coin.MCS_bought_cnt < MAX_BOUGHT_CNT else 0)}) '
                          f' ({set_dif_color(candles[0]["trade_price"], coin.avg_buy_price)}) ')

                # 매도 조건
                # 시간 캔들이 바뀐 경우
                if coin.check_time != now:
                    if i == 0:
                        print(f'----------------------------------- UPDATE ---------------------------------------'
                              f'\n{coin.check_time} -> \033[36m{now}\033[0m')

                    if coin.status in [Status.BOUGHT, Status.ADDBUY] or coin.MCS_bought_cnt != 0:
                        sell_result = coin.sell_coin()
                        print(f'\033[104m{get_now_time()} {coin.name:>6}(  SELL)| {int(round(get_sell_price(sell_result)))}원\033[0m')
                        log_file.write(f'{get_now_time()}, {coin.name}, SELL, {int(round(get_sell_price(sell_result)))}\n')

                    coin.status = Status.WAIT
                    coin.max_earnings_ratio = 0
                    coin.earnings_ratio = 0
                    coin.check_time = now
                    coin.variability = candles[1]['high_price'] - candles[1]['low_price']
                    coin.high_price = candles[0]["opening_price"]

                    print(coin.variability, coin.high_price * 0.015)
                    if coin.variability < coin.high_price * 0.015:
                        coin.status = Status.PASS
                    coin.avg_buy_price = 0

                    coin.MCS_bought_cnt = 0
                    coin.MCS_buy_price = [candles[0]["opening_price"] - coin.variability * var * BUY_DIF_RANGE for var in range(1, MAX_BOUGHT_CNT + 1)]
                    print(coin.MCS_buy_price)

                    if i == len(coin_dict) - 1:
                        print(f'---------------------------------------------------------------------------------')
                else:  # 시간이 동일하다면
                    if coin.MCS_bought_cnt >= MAX_BOUGHT_CNT\
                            or candles[0]['trade_price'] > coin.MCS_buy_price[coin.MCS_bought_cnt]\
                            or coin.status == Status.PASS:
                        continue

                    # 매수
                    buy_result = coin.buy_coin(price=BUY_AMOUNT)
                    coin.MCS_bought_cnt += 1
                    if not buy_result:
                        continue
                    print(f'\033[101m{get_now_time()} {coin.name:>6}(  BUY{coin.MCS_bought_cnt})| {coin.bought_amount}원\033[0m')
                    log_file.write(f'{get_now_time()}, {coin.name}, BUY{coin.MCS_bought_cnt}, {coin.bought_amount}\n')
            except IndexError as e:
                continue


def set_state_color(state) -> str:
    if state == Status.BOUGHT:
        return f'\033[91m{state.name:>6}\033[0m'
    elif state == Status.ADDBUY:
        return f'\033[96m{state.name:>6}\033[0m'
    else:
        return f'{state.name:>6}'


def set_dif_color(a, b) -> str:
    if b == 0:
        return f'{0:>6.2f}%'
    value = (a - b) / a * 100
    if value <= 0:
        return f'\033[34m{value:>6.2f}%\033[0m'
    else:
        return f'\033[31m{value:>6.2f}%\033[0m'


if __name__ == '__main__':
    min_catch_strategy(get_market_code(div_cnt=COIN_DIV_CNT, maximum=COIN_MAXIMUM)[COIN_DIV_SELECT])
