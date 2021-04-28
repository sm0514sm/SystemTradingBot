import uuid
import jwt
import requests
import configparser
from function.order_stock import buy_stock
from function.get_market_code import get_market_code
from function.get_account import get_krw

config = configparser.ConfigParser()
config.read('config.ini', encoding='UTF8')
try:
    access_key: str = config['UPBIT']['UPBIT_OPEN_API_ACCESS_KEY']
    secret_key: str = config['UPBIT']['UPBIT_OPEN_API_SECRET_KEY']
except KeyError:
    config.read('../config.ini', encoding='UTF8')
    access_key: str = config['UPBIT']['UPBIT_OPEN_API_ACCESS_KEY']
    secret_key: str = config['UPBIT']['UPBIT_OPEN_API_SECRET_KEY']


if __name__ == "__main__":
    markets = get_market_code()[0]
    volume = get_krw() / len(markets) / 1.2
    print(f"* now KRW: {get_krw()}")
    print(f"* coin cnt: {len(markets)}")
    print(f"* volume: {volume}")
    # 모든 코인 구입하기
    for market in markets:
        buy_stock(f"KRW-{market}", price=volume, sleep=0)
    print(f"* now KRW: {get_krw()}")
    print(f"* coin cnt: {len(markets)}")
    print(f"* volume: {volume}")
