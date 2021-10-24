import pyupbit
from object.Coin import Coin, CmmStatus
from trading_connector.AbstractTradingConnector import AbstractTradingConnector
from util.MethodLoggerDecorator import method_logger_decorator, my_timer
import configparser
import sys
import os


class CoinTradingConnector(AbstractTradingConnector):
    def __init__(self):
        super().__init__()
        if not self.check_config():
            self.logger.error("coin_config.ini 파일이 유효하지 않아 프로그램을 종료합니다.")
            exit(-1)
        config = configparser.ConfigParser()
        config.read(f'{sys.path[1]}/config/coin_config.ini', encoding='UTF8')
        upbit_config = config['UPBIT']
        access = upbit_config.get("UPBIT_OPEN_API_ACCESS_KEY")
        secret = upbit_config.get("UPBIT_OPEN_API_SECRET_KEY")
        self.upbit = pyupbit.Upbit(access, secret)
        self.cmm_config = config['CMM']

    @method_logger_decorator
    def check_config(self) -> bool:
        config = configparser.ConfigParser()
        if not os.path.isfile(f'{sys.path[1]}/config/coin_config.ini'):
            self.logger.error("coin_config.ini 파일이 없습니다.")
            return False
        config.read(f'{sys.path[1]}/config/coin_config.ini', encoding='UTF8')
        upbit_config = config['UPBIT']
        access = upbit_config.get("UPBIT_OPEN_API_ACCESS_KEY")
        secret = upbit_config.get("UPBIT_OPEN_API_SECRET_KEY")
        if not access or len(access) != 40:
            self.logger.error("UPBIT_OPEN_API_ACCESS_KEY 가 없거나 유효하지 않습니다.")
            return False
        if not secret or len(secret) != 40:
            self.logger.error("UPBIT_OPEN_API_SECRET_KEY 가 없거나 유효하지 않습니다.")
            return False
        return True

    @method_logger_decorator
    def ready_trading(self):
        pass

    @method_logger_decorator
    def get_balances(self) -> list:
        return self.upbit.get_balances()

    @method_logger_decorator
    def buy(self, name, price_amount):

        pass

    @method_logger_decorator
    def sell(self, name, count_amount):
        pass

    @method_logger_decorator
    def get_current_price(self, name):
        pass

    @method_logger_decorator
    def set_current_prices(self, coins: list[Coin]):
        if len(coins) >= 100:
            current_price = pyupbit.get_current_price(['KRW-' + coin.name for coin in coins[:100]])
            current_price.update(pyupbit.get_current_price(['KRW-' + coin.name for coin in coins[100:]]))
        else:
            current_price = pyupbit.get_current_price(['KRW-' + coin.name for coin in coins])
        print(current_price)
        for coin in coins:
            coin.current_price = current_price['KRW-' + coin.name]

    @method_logger_decorator
    def set_min_max(self, coins: list[Coin]):
        for coin in coins:
            ohlcv = pyupbit.get_ohlcv("KRW-" + coin.name, interval='day', count=self.cmm_config.getint("COUNT"))
            coin.set_cmm_info(min(ohlcv['low']), max(ohlcv['high']))

    @method_logger_decorator
    def get_balance(self, name="KRW"):
        pass

    @method_logger_decorator
    def get_avg_buy_price(self, name):
        pass

    @method_logger_decorator
    def get_watching_list(self):
        coin_names = pyupbit.get_tickers(fiat="KRW")
        self.logger.info(f'{len(coin_names)}개의 코인 확인')
        return [coin_name[4:] for coin_name in coin_names]

    @method_logger_decorator
    def make_obj_list(self, names) -> list:
        return [Coin(name) for name in names]

    @method_logger_decorator
    def add_bought_stock_info(self, coin_list):
        my_stocks_info = self.get_balances()
        for my_stock_info in my_stocks_info:
            if my_stock_info['currency'] == 'KRW':
                continue
            for coin in coin_list:
                if coin.name == my_stock_info['currency']:
                    coin.status = CmmStatus.BOUGHT
                    coin.avg_buy_price = float(my_stock_info['avg_buy_price'])
                    coin.buy_volume = float(my_stock_info['balance'])
                    break
            else:
                self.logger.warning(f"{my_stock_info['currency']}을 coin_list에서 찾을 수 없습니다.")


if __name__ == "__main__":
    conn = CoinTradingConnector()
    watching_list = conn.get_watching_list()
    obj_list = conn.make_obj_list(watching_list)
    conn.add_bought_stock_info(obj_list)
    for obj in obj_list:
        print(obj.name, obj.status)
