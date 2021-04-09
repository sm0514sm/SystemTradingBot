import os
from Coin import Coin, State
from function.get_candles import get_candles
from function.get_now_time import get_now_time
from function.order_stock import *
from function.print_your_config import print_order_config
from function.get_market_code import get_market_code
from function.get_account import *


config = configparser.ConfigParser()
config.read('config.ini', encoding='UTF8')

MCS_order_config = config['MCS_ORDER']
candle_type: str = MCS_order_config.get('CANDLE_TYPE')
unit: int = MCS_order_config.getint('MINUTE_CANDLE_UNIT')

coin_div_cnt: int = MCS_order_config.getint('COIN_DIV_CNT')
coin_div_select: int = MCS_order_config.getint('COIN_DIV_SELECT')
coin_maximum: int = MCS_order_config.getint('COIN_MAXIMUM')

maximum_bought_cnt: int = MCS_order_config.getint('MAXIMUM_BOUGHT_CNT')
buy_dif_range: float = MCS_order_config.getfloat('BUY_DIF_RANGE')
buy_amount: int = MCS_order_config.getint('BUY_AMOUNT')


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
            candles = get_candles('KRW-' + coin.coin_name, count=2, minute=unit, candle_type=candle_type)
            coin.high_price = max(candles[0]["trade_price"], coin.high_price)
            now = candles[0]['candle_date_time_kst']
            print(f'{get_now_time()} {coin.coin_name:>6}({set_state_color(coin.state)}{coin.MCS_bought_cnt})| '
                  f'목표 가: {coin.MCS_buy_price[coin.MCS_bought_cnt] if coin.MCS_bought_cnt < maximum_bought_cnt else 0:>11.2f}, '
                  f'현재 가: {candles[0]["trade_price"]:>10},'
                  f'구매 가: {coin.avg_buy_price:>11.2f}'
                  f' ({set_dif_color(candles[0]["trade_price"], coin.MCS_buy_price[coin.MCS_bought_cnt])}) '
                  f' ({set_dif_color(candles[0]["trade_price"], coin.avg_buy_price)}) ')

            # 매도 조건
            # 시간 캔들이 바뀐 경우
            if coin.check_time != now:
                if i == 0:
                    print(f'----------------------------------- UPDATE ---------------------------------------'
                          f'\n{coin.check_time} -> \033[36m{now}\033[0m')

                if coin.state in [State.BOUGHT, State.ADDBUY]:
                    sell_result = coin.sell_coin()
                    print(f'\033[104m{get_now_time()} {coin.coin_name:>6}(  SELL)| {int(round(get_sell_price(sell_result)))}원\033[0m')
                    log_file.write(f'{get_now_time()}, {coin.coin_name}, SELL, {int(round(get_sell_price(sell_result)))}\n')

                coin.state = State.WAIT
                coin.max_earnings_ratio = 0
                coin.earnings_ratio = 0
                coin.check_time = now
                coin.variability = candles[1]['high_price'] - candles[1]['low_price']
                coin.high_price = candles[0]["opening_price"]
                if coin.variability < coin.high_price * 0.02:
                    coin.state = State.PASS
                coin.avg_buy_price = 0

                coin.MCS_bought_cnt = 0
                coin.MCS_buy_price = [candles[0]["opening_price"] - coin.variability * var * buy_dif_range for var in range(1, maximum_bought_cnt + 1)]
                print(coin.MCS_buy_price)

                if i == len(coin_dict) - 1:
                    print(f'---------------------------------------------------------------------------------')
            else:  # 시간이 동일하다면
                if candles[0]['trade_price'] > coin.MCS_buy_price[coin.MCS_bought_cnt] or coin.MCS_bought_cnt >= maximum_bought_cnt:
                    continue

                # 매수
                buy_result = coin.buy_coin(price=buy_amount)
                coin.MCS_bought_cnt += 1
                if not buy_result:
                    continue
                print(f'\033[101m{get_now_time()} {coin.coin_name:>6}(  BUY{coin.MCS_bought_cnt})| {coin.bought_amount}원\033[0m')
                log_file.write(f'{get_now_time()}, {coin.coin_name}, BUY{coin.MCS_bought_cnt}, {coin.bought_amount}\n')


def set_state_color(state) -> str:
    if state == State.BOUGHT:
        return f'\033[91m{state.name:>6}\033[0m'
    elif state == State.ADDBUY:
        return f'\033[96m{state.name:>6}\033[0m'
    else:
        return f'{state.name:>6}'


def set_dif_color(a, b) -> str:
    if b == 0:
        return f'{0:>6.2f}%'
    value = (a - b) / a * 100
    if value < 0:
        return f'\033[34m{value:>6.2f}%\033[0m'
    else:
        return f'\033[31m{value:>6.2f}%\033[0m'


if __name__ == '__main__':
    min_catch_strategy(get_market_code(div_cnt=coin_div_cnt, maximum=coin_maximum)[coin_div_select])
