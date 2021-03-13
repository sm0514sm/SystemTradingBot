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

VM_order_config = config['VB_ORDER']
candle_type: str = VM_order_config.get('CANDLE_TYPE')
unit: int = VM_order_config.getint('MINUTE_CANDLE_UNIT')
percent_buy_range: int = VM_order_config.getint('PERCENT_OF_BUY_RANGE')


def volatility_strategy(coin_name):
    while True:
        candles = get_candles('KRW-' + coin_name, count=2, minute=unit)
        now = candles[0]['candle_date_time_kst']
        print(f'{now=}')
        # last_range = 전봉 고가 - 전봉 저가
        last_range = candles[1]['high_price'] - candles[1]['low_price']
        if last_range == 0:
            continue
        buy_price = candles[0]["opening_price"] + last_range * (percent_buy_range / 100)
        while True:
            new_candle = get_candles('KRW-' + coin_name, 1, 0.06, unit)[0]
            if new_candle['candle_date_time_kst'] != now:
                break
            print(f'{buy_price:.2f} 이상 < {new_candle["trade_price"]=}')
            if new_candle["trade_price"] < buy_price:
                continue
            # 매수
            buy_result = buy_stock(access_key, secret_key, market="KRW-" + coin_name, price=10000)
            print(f'{buy_result=}')
            while get_candles('KRW-' + coin_name, 1, 0.06, unit)[0]['candle_date_time_kst'] == now:
                continue

            # 매수 개수 확인
            accounts = []
            for _ in range(10):
                time.sleep(1)
                accounts = get_account(access_key, secret_key)
                if accounts[0].get('balance'):
                    break
            krw_bought = float(accounts[0].get('balance'))
            avg_price = float(buy_result.get('price'))
            coin_volume = 0

            for coin_kind in accounts:
                if coin_kind['currency'] == coin_name:
                    coin_volume = coin_kind['balance']

            # 매도
            sell_result = sell_stock(access_key, secret_key, market="KRW-" + coin_name, volume=coin_volume)
            print(f'{sell_result=}')


if __name__ == '__main__':
    volatility_strategy('MBL')
