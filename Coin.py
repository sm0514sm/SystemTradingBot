import configparser
import time
from function.order_stock import buy_stock
from function.order_stock import sell_stock
from function.get_account import get_account
from enum import IntEnum

config = configparser.ConfigParser()
config.read('config.ini', encoding='UTF8')

access_key: str = config['UPBIT']['UPBIT_OPEN_API_ACCESS_KEY']
secret_key: str = config['UPBIT']['UPBIT_OPEN_API_SECRET_KEY']


class State(IntEnum):
    WAIT = 1
    BOUGHT = 2
    SOLD = 3


class Coin:
    def __init__(self, coin_name: str):
        self.coin_name: str = coin_name
        self.check_time: str = ""
        self.balance: float = 0
        self.state: IntEnum = State.WAIT
        self.variability: float = 0
        self.buy_price: float = 0

    # 매수 개수 확인
    def update_balance(self):
        for _ in range(10):
            time.sleep(0.5)
            for account in get_account(access_key, secret_key):
                if account.get('currency') == self.coin_name:
                    self.balance = account.get('balance')
                    break
            if self.balance:
                break

    def buy_coin(self, price):
        buy_result = buy_stock(access_key, secret_key, f'KRW-{self.coin_name}', price=price, sleep=3)
        print(buy_result)
        self.state = State.BOUGHT
        return buy_result

    def sell_coin(self):
        if self.state != State.BOUGHT:
            return "Not bought"
        self.update_balance()
        sell_result = sell_stock(access_key, secret_key, f'KRW-{self.coin_name}', self.balance, sleep=3)
        print(sell_result)
        self.state = State.WAIT
        return sell_result.get('uuid')
