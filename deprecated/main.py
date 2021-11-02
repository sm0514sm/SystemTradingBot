import jwt
import json
import uuid
import hashlib
from urllib.parse import urlencode
import os
import configparser
import requests
import time
import timeit
import datetime
from function.get_account import get_account
from function.order_stock import buy_stock, sell_stock
from function.get_market_code import get_market_code
from function.get_now_time import get_now_time
from function.get_candles import get_candles
from function.get_now_coin_info import get_now_coin_info
from function.print_your_config import print_order_config
from timeit import default_timer

config = configparser.ConfigParser()
config.read('config.ini', encoding='UTF8')

access_key: str = config['UPBIT']['UPBIT_OPEN_API_ACCESS_KEY']
secret_key: str = config['UPBIT']['UPBIT_OPEN_API_SECRET_KEY']

SM_order_config = config['SM_ORDER']
coin_div_cnt: int = SM_order_config.getint('COIN_DIV_CNT')
coin_div_select: int = SM_order_config.getint('COIN_DIV_SELECT')
coin_maximum: int = SM_order_config.getint('COIN_MAXIMUM')
wait_time: float = SM_order_config.getfloat('WAIT_TIME')
check_count: int = SM_order_config.getint('CHECK_COUNT')
surge_STV_time: float = SM_order_config.getfloat('SURGE_STV_DETECTION_TIME')
percent_of_buying: float = SM_order_config.getfloat('PERCENTS_OF_BUYING')
percent_of_rising: float = SM_order_config.getfloat('DETERMINE_PERCENTS_OF_RISING')
percent_of_stop_loss: float = SM_order_config.getfloat('PERCENT_OF_STOP_LOSS')


def auto_order(coin: dict, price: float):
    print(f'{get_now_time()} [KRW-{coin.get("name")}] {int(price)}원 주문')
    buy_result = buy_stock(access_key, secret_key, market="KRW-" + coin['name'], price=price)
    accounts = []
    for _ in range(10):
        time.sleep(1)
        accounts = get_account(access_key, secret_key)
        if accounts[0].get('balance'):
            break
    krw_bought = float(accounts[0].get('balance'))
    avg_price = float(buy_result.get('price'))
    stop_loss_price = avg_price * (100 - percent_of_stop_loss) / 100
    for coin_kind in accounts:
        if coin_kind['currency'] == coin['name']:
            coin['balance'] = coin_kind['balance']
    check_time = timeit.default_timer()

    while timeit.default_timer() - check_time >= wait_time:
        if stop_loss_price >= get_now_coin_info(f'KRW-{coin.get("name")}', sleep=0.5).get('trade_price'):
            break

    sell_result = sell_stock(access_key, secret_key, market="KRW-" + coin['name'], volume=coin['balance'])
    accounts = get_account(access_key, secret_key)
    krw_sold = float(accounts[0].get('balance'))

    os.makedirs('logs', exist_ok=True)
    with open("logs/order.log", "a") as f:
        f.write(
            f'{get_now_time()} [KRW-{coin.get("name")}] 산 금액: {int(krw_before - krw_bought)}원, 판 금액: {int(krw_sold - krw_bought)}원, '
            f'손익: {int(krw_sold - krw_before)}원 '
            f'({int(krw_sold - krw_bought) / int(krw_before - krw_bought) * 100 - 100:.3f}%)\n'
        )
    print(
        f'{get_now_time()} [KRW-{coin.get("name")}] 산 금액: {int(krw_before - krw_bought)}원, 판 금액: {int(krw_sold - krw_bought)}원, '
        f'손익: {int(krw_sold - krw_before)}원 '
        f'({int(krw_sold - krw_bought) / int(krw_before - krw_bought) * 100 - 100:.3f}%)'
    )


if __name__ == '__main__':
    print_order_config(config.items(section="SM_ORDER"))

    # 주문 가격 결정

    coin_accounts: list = get_account(access_key, secret_key)
    krw_before = float(coin_accounts[0].get('balance'))
    price_per_order = max(6000.0, krw_before * percent_of_buying / 100)
    # 주문할 코인 결정
    coin_names = get_market_code(div_cnt=coin_div_cnt, maximum=coin_maximum)[coin_div_select]
    print(coin_names)
    # coin_names = ["IOTA", "BTC"]
    # 코인 모니터링
    while True:
        print(f'{get_now_time()} interval')
        print(coin_names)
        for coin_name in coin_names:
            minute_candles = get_candles(market="KRW-" + coin_name, count=check_count, sleep=0.06)
            if not minute_candles:
                continue
            stv_list = [minute_candle['candle_acc_trade_volume'] for minute_candle in minute_candles[1:]]
            start_time = datetime.datetime.strptime(minute_candles[0]['candle_date_time_kst'], '%Y-%m-%dT%H:%M:%S')
            now_time = datetime.datetime.fromtimestamp(minute_candles[0]['timestamp'] / 1000)

            print(now_time, datetime.datetime.now(), (now_time - datetime.datetime.now()).total_seconds())
            if abs((now_time - datetime.datetime.now()).total_seconds()) >= 7:
                print('버림', coin_name)
                coin_names.remove(coin_name)
                continue
            if abs((now_time - datetime.datetime.now()).total_seconds()) >= 3:
                continue
            # 판단 1. 거래량 급증 탐지시간이내
            if (now_time - start_time).total_seconds() >= surge_STV_time:
                # print(f'1. {(now_time - start_time).total_seconds()=} < {surge_STV_time=}')
                continue
            # 판단 2. 거래량이 이전 분 캔들 조회 리스트 중 가장 큰 값보다 초과
            if minute_candles[0]['candle_acc_trade_volume'] <= max(stv_list):
                continue
            # 판단 3. 이전 분 캔들 종가 * 상승 판단 비율 보다 현재 가격이 높음
            if minute_candles[0]['trade_price'] <= minute_candles[1]['trade_price'] * (100 + percent_of_rising) / 100:
                continue
            print(f'1. {(now_time - start_time).total_seconds()=} < {surge_STV_time=}')
            print(f"2. {minute_candles[0]['candle_acc_trade_volume']=} > {max(stv_list)=}")
            print(
                f"3. {minute_candles[0]['trade_price']=} > {minute_candles[1]['trade_price'] * (100 + percent_of_rising) / 100=}"
                f"({minute_candles[1]['trade_price']=})")
            # 코인 주문
            coin_order = dict()
            coin_order['name'] = coin_name
            auto_order(coin=coin_order, price=price_per_order)

            # 주문 가격 결정
            coin_accounts: list = get_account(access_key, secret_key)
            krw_before = float(coin_accounts[0].get('balance'))
            price_per_order = max(6000.0, krw_before * percent_of_buying / 100)
            break
