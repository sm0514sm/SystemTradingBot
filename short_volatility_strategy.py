import os
import configparser
import requests
import time
import datetime
from Coin import Coin, State
from function.get_account import get_account
from function.order_stock import *
from function.get_market_code import get_market_code
from function.get_now_time import get_now_time
from function.get_candles import get_candles
from function.get_now_coin_info import get_now_coin_info
from function.print_your_config import print_order_config
from timeit import default_timer

config = configparser.ConfigParser()
config.read('config.ini', encoding='UTF8')

VM_order_config = config['VB_ORDER']
candle_type: str = VM_order_config.get('CANDLE_TYPE')
unit: int = VM_order_config.getint('MINUTE_CANDLE_UNIT')
percent_buy_range: int = VM_order_config.getint('PERCENT_OF_BUY_RANGE')
percent_of_buying: int = VM_order_config.getint('PERCENTS_OF_BUYING')  # 추가


def short_volatility_strategy(coins_name: list):
    print_order_config(config.items(section="VB_ORDER"))
    coin_dict = dict()
    for coin_name in coins_name:
        coin_dict[coin_name] = Coin(coin_name)
    while True:
        for coin in coin_dict.values():
            candles = get_candles('KRW-' + coin.coin_name, count=2, minute=unit)
            now = candles[0]['candle_date_time_kst']
            print(f'{get_now_time()} {coin.coin_name}({set_state_color(coin.state)})| '
                  f'목표 가: {coin.buy_price:>11.2f}, 현재 가: {candles[0]["trade_price"]:>10}'
                  f' ({set_dif_color(candles[0]["trade_price"], coin.buy_price)})')

            if coin.check_time != now:
                print(f'{coin.check_time} -> \033[36m{now}\033[0m')
                if coin.state == State.BOUGHT or coin.state == State.TRYBUY:
                    sell_result = coin.sell_coin()
                    if sell_result == "Not bought":
                        print(f'\033[100m{get_now_time()} {coin.coin_name}( ERROR)|\033[0m')
                    else:
                        print(f'\033[104m{get_now_time()} {coin.coin_name}(  SELL)| '
                              f'{int(get_total_sell_price(access_key))}\033[0m')
                        with open("logs/VB_order.log", "a") as f:
                            f.write(f'{get_now_time()} {coin.coin_name}(  SELL)| '
                                    f'{int(get_total_sell_price(access_key))}원\n')
                    if coin.state == State.TRYBUY:
                        coin.cansel_buy()
                        print(f'\033[104m{get_now_time()} {coin.coin_name}( CANCEL)|\033[0m')
                coin.check_time = now
                coin.variability = candles[1]['high_price'] - candles[1]['low_price']
                coin.buy_price = candles[0]["opening_price"] + coin.variability * (percent_buy_range / 100)
            else:  # 시간이 동일하다면
                if coin.state == State.BOUGHT or coin.variability == 0:
                    continue
                if candles[0]['trade_price'] <= coin.buy_price:
                    continue

                # 매수
                limit = True
                buy_result = coin.buy_coin(price=10000, limit=limit)
                os.makedirs('logs', exist_ok=True)
                if limit:
                    print(f'\033[95m{get_now_time()} {coin.coin_name}(TRYBUY)| '
                          f'{buy_result.get("locked"):>6}원\033[0m')
                    with open("logs/VB_order.log", "a") as f:
                        f.write(f'{get_now_time()} {coin.coin_name}(TRYBUY)| '
                                f'{buy_result.get("locked"):>6}원\033[0m')
                else:
                    print(f'\033[101m{get_now_time()} {coin.coin_name}(   BUY)| '
                          f'{int(get_total_buy_price(coin.coin_name))}원\033[0m')
                    with open("logs/VB_order.log", "a") as f:
                        f.write(f'{get_now_time()} {coin.coin_name}(   BUY)| '
                                f'{int(get_total_buy_price(coin.coin_name))}원\n')


def set_state_color(state) -> str:
    if state == State.BOUGHT:
        return f'\033[91m{state.name:>6}\033[0m'
    else:
        return f'{state.name:>6}'


def set_dif_color(a, b) -> str:
    value = (a - b) / a * 100
    if value < 0:
        return f'\033[34m{value:>6.2f}%\033[0m'
    else:
        return f'\033[31m{value:>6.2f}%\033[0m'


if __name__ == '__main__':
    short_volatility_strategy(['BTC'])
