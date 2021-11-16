import datetime
import pickle
import time

import pyupbit
from object.Coin import Coin, CmmStatus
from trading_connector.AbstractTradingConnector import AbstractTradingConnector
from util.Calculator import calculate_rate
from util.DiscordConnector import DiscordConnector
from util.MethodLoggerDecorator import method_logger_decorator, my_timer
import configparser
import sys
import os


def calculate_avg_sell_price(trades: list) -> float:
    total_price = sum(map(lambda trade: float(trade.get('price')) * float(trade.get('volume')), trades))
    total_volume = sum(map(lambda trade: float(trade.get('volume')), trades))
    return total_price / total_volume


def calculate_total_amount(log: dict) -> float:
    trades = log.get('trades')
    total_price = sum(map(lambda trade: float(trade.get('price')) * float(trade.get('volume')), trades))
    return total_price - float(log.get('paid_fee'))


class CoinTradingConnector(AbstractTradingConnector):
    def __init__(self):
        super().__init__()
        config = self.check_config()
        if not config:
            self.logger.error("coin_config.ini 파일이 유효하지 않아 프로그램을 종료합니다.")
            exit(-1)
        upbit_config = config['UPBIT']
        self.access = upbit_config.get("UPBIT_OPEN_API_ACCESS_KEY")
        self.secret = upbit_config.get("UPBIT_OPEN_API_SECRET_KEY")

        discord_config = config['DISCORD']
        self.webhook = discord_config.get("DISCORD_WEBHOOK_URL")
        self.heartbeat_interval = int(discord_config.get("HEARTBEAT_INTERVAL"))

        self.upbit = pyupbit.Upbit(self.access, self.secret)
        self.cmm_config = dict(config['CMM'])
        self.cmm_config['interval'] = self.cmm_config['interval']
        self.cmm_config['count'] = int(self.cmm_config['count'])
        self.cmm_config['max_dca_buy_cnt'] = int(self.cmm_config['max_dca_buy_cnt'])
        self.cmm_config['dca_buy_rate'] = int(self.cmm_config['dca_buy_rate'])
        self.cmm_config['value_k'] = float(self.cmm_config['value_k'])
        self.cmm_config['delay'] = int(self.cmm_config['delay'])
        self.cmm_config['buy_amount'] = int(self.cmm_config['buy_amount'])
        self.cmm_config['profit_rate'] = int(self.cmm_config['profit_rate'])

        self.discord_conn = DiscordConnector(self.cmm_config, webhook_url=self.webhook)

    @method_logger_decorator
    def check_config(self):
        config = configparser.ConfigParser()
        if not os.path.isfile(f'{sys.path[1]}/config/coin_config.ini'):
            if not os.path.isfile(f'config/coin_config.ini'):
                self.logger.error(f'{sys.path[1]}/config/coin_config.ini 파일이 없습니다.')
                return None
            else:
                config.read(f'config/coin_config.ini', encoding='UTF8')
        else:
            config.read(f'{sys.path[1]}/config/coin_config.ini', encoding='UTF8')

        upbit_config = config['UPBIT']
        access = upbit_config.get("UPBIT_OPEN_API_ACCESS_KEY")
        secret = upbit_config.get("UPBIT_OPEN_API_SECRET_KEY")
        if not access or len(access) != 40:
            self.logger.error("UPBIT_OPEN_API_ACCESS_KEY 가 없거나 유효하지 않습니다.")
            return None
        if not secret or len(secret) != 40:
            self.logger.error("UPBIT_OPEN_API_SECRET_KEY 가 없거나 유효하지 않습니다.")
            return None
        return config

    @method_logger_decorator
    def ready_trading(self):
        self.discord_conn.post(self.discord_conn.start_data())

    @method_logger_decorator
    def heartbeat(self):
        now_timestamp = datetime.datetime.now().timestamp()
        now_timestamp = now_timestamp - now_timestamp % (self.heartbeat_interval * 60)
        print(now_timestamp, self.last_hb_time)
        if not self.last_hb_time or self.last_hb_time != now_timestamp:
            self.last_hb_time = now_timestamp
            self.discord_conn.post(self.discord_conn.heart_data(self.get_total_assets()))

    @method_logger_decorator
    def get_total_assets(self) -> float:
        total_assets = 0
        watching_list = self.get_watching_list()
        for balance in self.get_balances():
            currency = balance.get('currency')
            if currency == 'KRW':
                current_price = 1
            elif currency not in watching_list:
                current_price = 0
            else:
                current_price = pyupbit.get_current_price(f"KRW-{currency}")
            total_assets += current_price * float(balance.get('balance'))
        return total_assets

    @method_logger_decorator
    def get_balances(self) -> list:
        return self.upbit.get_balances()

    @method_logger_decorator
    def buy(self, coin: Coin, price_amount) -> bool:
        order_log = self.upbit.buy_market_order(f"KRW-{coin.name}", price_amount)
        print(order_log)
        uuid = order_log.get('uuid')
        if not uuid:
            self.logger.warning(order_log)
            return False
        while uuid and self.upbit.get_order(uuid).get('state') != 'done':
            time.sleep(1)
        coin.status = CmmStatus.BOUGHT
        coin.dca_buy_cnt += 1
        coin.bought_amount += price_amount
        coin.avg_buy_price = float(self.get_balance_info(coin.name).get('avg_buy_price'))
        coin.buy_volume_cnt = float(self.get_balance_info(coin.name).get('balance'))
        self.discord_conn.post(self.discord_conn.buy_data(coin))
        return True

    @method_logger_decorator
    def sell(self, coin: Coin, count_amount) -> bool:
        order_log = self.upbit.sell_market_order(f"KRW-{coin.name}", count_amount)
        print(order_log)
        uuid = order_log.get('uuid')
        if not uuid:
            self.logger.warning(order_log)
            return False
        while uuid and self.upbit.get_order(uuid).get('state') == 'wait':
            time.sleep(1)
        self.logger.debug(f"{order_log=}")

        coin.avg_sell_price = calculate_avg_sell_price(order_log.get('trades'))
        coin.sold_amount = calculate_total_amount(order_log)
        self.logger.info(f'매수가: {coin.avg_buy_price}, 매도가: {coin.avg_sell_price}, '
                         f'수익률: {calculate_rate(coin.avg_sell_price, coin.avg_buy_price)}')
        self.discord_conn.post(self.discord_conn.sell_data(coin))
        coin.status = CmmStatus.WAIT
        coin.dca_buy_cnt = 0
        coin.bought_amount = 0
        coin.avg_buy_price = 0
        coin.buy_volume_cnt = 0
        coin.avg_sell_price = 0
        coin.sold_amount = 0
        return True

    def set_current_prices(self, coins: list[Coin]):
        if len(coins) >= 100:
            current_price = pyupbit.get_current_price(['KRW-' + coin.name for coin in coins[:100]])
            current_price.update(pyupbit.get_current_price(['KRW-' + coin.name for coin in coins[100:]]))
        else:
            current_price = pyupbit.get_current_price(['KRW-' + coin.name for coin in coins])
        for coin in coins:
            coin.current_price = current_price['KRW-' + coin.name]

    def apply_pickles(self, stock_list: list, strategy_name: str) -> list:
        pickle_name = f"coins_{strategy_name}.pickle"
        if os.path.isfile(pickle_name):
            self.logger.info(f"{pickle_name}로부터 데이터 읽어들임")
            with open(pickle_name, 'rb') as f:
                stock_list = pickle.load(f)
        else:
            self.logger.info(f"{pickle_name}가 없습니다")
        return stock_list

    def save_pickles(self, stock_list: list, strategy_name: str):
        pickle_name = f"coins_{strategy_name}.pickle"
        with open(pickle_name, 'wb') as f:
            pickle.dump(stock_list, f, pickle.HIGHEST_PROTOCOL)

    def set_min_max(self, coins: list[Coin]):
        for coin in coins:
            ohlcv = pyupbit.get_ohlcv("KRW-" + coin.name, interval='day', count=self.cmm_config["count"])
            coin.set_cmm_info(min(ohlcv['low']), max(ohlcv['high']))

    @method_logger_decorator
    def get_balance_info(self, name: str = "KRW"):
        for balance in self.upbit.get_balances():
            if balance.get('currency') == name:
                return balance
        else:
            self.logger.warning(f'{name}을 찾을 수 없습니다.')

    @method_logger_decorator
    def get_balance(self, name: str = "KRW"):
        if name == "KRW":
            return self.upbit.get_balance("KRW")
        return self.upbit.get_balance(f"KRW-{name}")

    @method_logger_decorator
    def get_balance(self, coin: Coin | str):
        if type(coin) == Coin:
            name = coin.name
        else:
            name = coin
        if not name or name == "KRW":
            return self.upbit.get_balance("KRW")
        return self.upbit.get_balance(f"KRW-{name}")

    @method_logger_decorator
    def get_watching_list(self):
        coin_names = pyupbit.get_tickers(fiat="KRW")
        return [coin_name[4:] for coin_name in coin_names]

    @method_logger_decorator
    def make_obj_list(self, names) -> list:
        return [Coin(name) for name in names]

    @method_logger_decorator
    def add_bought_stock_info(self, coin_list):
        # TODO 내 계좌에 없고 pickle에만 남아있는 코인 초기화
        my_stocks_info = self.get_balances()
        for my_stock_info in my_stocks_info:
            if my_stock_info['currency'] == 'KRW':
                continue
            for coin in coin_list:
                if coin.name == my_stock_info['currency']:
                    coin.status = CmmStatus.BOUGHT
                    coin.avg_buy_price = float(my_stock_info['avg_buy_price'])
                    coin.buy_volume_cnt = float(my_stock_info['balance'])
                    if coin.dca_buy_cnt == 0:
                        coin.dca_buy_cnt = 1
                    break
            else:
                self.logger.warning(f"{my_stock_info['currency']}을 coin_list에서 찾을 수 없습니다.")


if __name__ == "__main__":
    conn = CoinTradingConnector()
    watching_list2 = conn.get_watching_list()
    obj_list = conn.make_obj_list(watching_list2)
    conn.add_bought_stock_info(obj_list)
    for obj in obj_list:
        print(obj.name, obj.status)
    # conn.buy(Coin("XRP"), 5050)
    # conn.sell(Coin("XRP"), 3.44709897)
    print(conn.get_balance_info('BTT'))
    print(conn.get_balance_info('DAWN'))
    print(conn.get_balance_info('XRP'))
    print(conn.upbit.get_order('ae428351-7785-45e3-9905-f4dc19feeaf7'))
    print(conn.upbit.get_order('40faa4e2-28cd-49ba-8d98-05b220c01965'))
    calculate_avg_sell_price([{'market': 'KRW-XRP', 'uuid': '58922dba-122d-4252-958f-87f85e94563c', 'price': '1000.0',
                               'volume': '3', 'funds': '5032.7644962', 'created_at': '2021-11-07T23:21:46+09:00',
                               'side': 'ask'},
                              {'market': 'KRW-XRP', 'uuid': '58922dba-122d-4252-958f-87f85e94563c', 'price': '2000.0',
                               'volume': '1', 'funds': '5032.7644962', 'created_at': '2021-11-07T23:21:46+09:00',
                               'side': 'ask'}])
    # print(conn.upbit.get_balance("KRW-BTC"))
    # print(conn.get_balance_info("BTC"))


# {'uuid': '126b7959-11d9-468c-9b1b-f429094c5da8', 'side': 'bid', 'ord_type': 'price', 'price': '5000.0', 'state': 'wait', 'market': 'KRW-BTC', 'created_at': '2021-10-26T23:04:55+09:00', 'volume': None, 'remaining_volume': None, 'reserved_fee': '2.5', 'remaining_fee': '2.5', 'paid_fee': '0.0', 'locked': '5002.5', 'executed_volume': '0.0', 'trades_count': 0, 'trades': []}
# {'uuid': '214e12a5-cd79-411c-9eb2-17e8b9ac6a8e', 'side': 'bid', 'ord_type': 'price', 'price': '5000.0', 'state': 'cancel', 'market': 'KRW-BTC', 'created_at': '2021-10-26T22:46:00+09:00', 'volume': None, 'remaining_volume': None, 'reserved_fee': '2.5', 'remaining_fee': '0.00037306', 'paid_fee': '2.49962694', 'locked': '0.74649306', 'executed_volume': '0.00006637', 'trades_count': 1, 'trades': [{'market': 'KRW-BTC', 'uuid': 'ee590cc6-65c1-47de-9e70-8d45f2782420', 'price': '75324000.0', 'volume': '0.00006637', 'funds': '4999.25388', 'created_at': '2021-10-26T22:46:00+09:00', 'side': 'bid'}]}
# sell log
# {'uuid': 'ae428351-7785-45e3-9905-f4dc19feeaf7', 'side': 'ask', 'ord_type': 'market', 'price': None, 'state': 'wait', 'market': 'KRW-XRP', 'created_at': '2021-11-07T23:21:46+09:00', 'volume': '3.44709897', 'remaining_volume': '3.44709897', 'reserved_fee': '0.0', 'remaining_fee': '0.0', 'paid_fee': '0.0', 'locked': '3.44709897', 'executed_volume': '0.0', 'trades_count': 0}
# {'uuid': 'ae428351-7785-45e3-9905-f4dc19feeaf7', 'side': 'ask', 'ord_type': 'market', 'price': None, 'state': 'done', 'market': 'KRW-XRP', 'created_at': '2021-11-07T23:21:46+09:00', 'volume': '3.44709897', 'remaining_volume': '0.0', 'reserved_fee': '0.0', 'remaining_fee': '0.0', 'paid_fee': '2.5163822481', 'locked': '0.0', 'executed_volume': '3.44709897', 'trades_count': 1, 'trades': [{'market': 'KRW-XRP', 'uuid': '58922dba-122d-4252-958f-87f85e94563c', 'price': '1460.0', 'volume': '3.44709897', 'funds': '5032.7644962', 'created_at': '2021-11-07T23:21:46+09:00', 'side': 'ask'}]}

def test_get_total_assets():
    print(CoinTradingConnector().get_total_assets())


def test_get_watching_list():
    print(CoinTradingConnector().get_watching_list())


def test_buy():
    con = CoinTradingConnector()
    con.buy(Coin("XRP"), 5050)


def test_heart_beat():
    a = CoinTradingConnector()
    for _ in range(100):
        a.heartbeat()
        time.sleep(3)


def test_heartbeat():
    a = 1 * 60
    print(a)
    for _ in range(100):
        b = datetime.datetime.now().timestamp()
        print(datetime.datetime.now(), b - b % a)
        time.sleep(1)
