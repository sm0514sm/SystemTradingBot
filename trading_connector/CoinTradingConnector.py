import configparser
import os
import pickle
import time
from datetime import datetime

import pyupbit
from object.Coin import Coin, Status
from trading_connector.AbstractTradingConnector import AbstractTradingConnector
from util.Calculator import calculate_rate
from util.DiscordConnector import DiscordConnector
from util.MethodLoggerDecorator import method_logger_decorator
from util.Reporter import Reporter
from util.SystemValue import *


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
        self.webhook_url = discord_config.get("DISCORD_WEBHOOK_URL")
        self.heartbeat_url = discord_config.get("DISCORD_HEARTBEAT_URL")
        self.heartbeat_interval = int(discord_config.get("HEARTBEAT_INTERVAL"))

        self.upbit = pyupbit.Upbit(self.access, self.secret)
        self.cmm_config = dict(config['CMM'])
        self.cmm_config['interval'] = self.cmm_config['interval']
        self.cmm_config['count'] = int(self.cmm_config['count'])
        self.cmm_config['max_dca_buy_cnt'] = int(self.cmm_config['max_dca_buy_cnt'])
        self.cmm_config['dca_buy_rate'] = int(self.cmm_config['dca_buy_rate'])
        self.cmm_config['value_k'] = float(self.cmm_config['value_k'])
        self.cmm_config['delay'] = int(self.cmm_config['delay'])
        self.cmm_config['start_amount'] = int(self.cmm_config['start_amount'])
        self.cmm_config['multiple_amount'] = int(self.cmm_config['multiple_amount'])
        self.cmm_config['profit_rate'] = int(self.cmm_config['profit_rate'])

        self.svb_config = dict(config['SVB'])
        self.svb_config['profit_rate'] = int(self.svb_config['profit_rate'])
        self.svb_config['buy_amount'] = int(self.svb_config['buy_amount'])

        self.discord_conn = DiscordConnector(self.cmm_config,
                                             webhook_url=self.webhook_url,
                                             heartbeat_url=self.heartbeat_url)
        self.hold_krw = float(self.get_balance_info()['balance'])
        self.reporter = Reporter()

    @method_logger_decorator
    def check_config(self):
        config = configparser.ConfigParser()
        config_path = f'{root_path()}/config/coin_config.ini'
        if not os.path.isfile(config_path):
            self.logger.error(f'{config_path} 파일이 없습니다.')
            return None
        config.read(f'{config_path}', encoding='UTF8')

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
        now_timestamp = datetime.now().timestamp()
        now_timestamp = now_timestamp - now_timestamp % (self.heartbeat_interval * 60)
        if not self.last_hb_time or self.last_hb_time != now_timestamp:
            self.last_hb_time = now_timestamp
            self.discord_conn.post_heartbeat(self.discord_conn.heart_data(self.get_total_assets()))

    def daily_at_9(self, stocks_list):
        now_timestamp = datetime.now().timestamp()
        now_timestamp = now_timestamp - now_timestamp % (60 * 60 * 24)
        if not self.last_report_time or self.last_report_time != now_timestamp:
            self.last_report_time = now_timestamp
            # DO
            self.logger.info("Daily Routine")
            self.daily_report()
            self.logger.info("1. 최소값과 최대값을 다시 계산합니다.")
            self.set_min_max(stocks_list)
            self.logger.info("2. 전날 거래량을 다시 계산합니다.")
            self.update_last_infos(stocks_list)
            # self.logger.info("3. 시가와 목표 구매가를 다시 계산합니다.")
            # stocks_list = list(map(setup_target_buy_price, stocks_list))
            self.logger.info("4. 현재 보유한 종목을 시장가에 팝니다.")
            self.sell_all(stocks_list)
            self.logger.info("5. 모든 종목의 상태를 WAIT으로 합니다.")
            setup_status_wait(stocks_list)

    @method_logger_decorator
    def daily_report(self):
        if self.reporter.add_report_data(datetime.today().strftime("%Y%m%d"), int(self.get_total_assets())):
            graph_file_name = self.reporter.make_daily_report()
            self.discord_conn.post_daily_report(self.discord_conn.daily_report_data(graph_file_name))

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
    def get_order(self, buy_uuid):
        return self.upbit.get_order(buy_uuid)

    @method_logger_decorator
    def cancel_order(self, buy_uuid):
        return self.upbit.cancel_order(buy_uuid)

    @method_logger_decorator
    def buy(self, coin: Coin, price_amount) -> bool:
        order_log = self.upbit.buy_market_order(f"KRW-{coin.name}", price_amount)
        uuid = order_log.get('uuid')
        coin.buy_uuid = uuid
        if not uuid:
            self.logger.warning(order_log)
            return False
        while uuid and self.upbit.get_order(uuid).get('state') == 'wait':
            time.sleep(1)
        self.logger.debug(f"{coin.name} buy {order_log=}")
        coin.status = Status.BOUGHT
        coin.dca_buy_cnt += 1
        coin.bought_amount += price_amount
        coin.avg_buy_price = float(self.get_balance_info(coin.name).get('avg_buy_price'))
        coin.buy_volume_cnt = float(self.get_balance_info(coin.name).get('balance'))
        self.hold_krw = float(self.get_balance_info()['balance'])
        return True

    @method_logger_decorator
    def buy_limit_order(self, coin: Coin, price, amount) -> bool:
        order_log = self.upbit.buy_limit_order(f"KRW-{coin.name}", price, amount)
        uuid = order_log.get('uuid')
        coin.buy_uuid = uuid
        if not uuid:
            self.logger.warning(order_log)
            return False
        coin.status = Status.TRY_BUY
        return True

    @method_logger_decorator
    def sell(self, coin: Coin, count_amount, status=Status.WAIT) -> bool:
        order_log = self.upbit.sell_market_order(f"KRW-{coin.name}", count_amount)
        uuid = order_log.get('uuid')
        if not uuid:
            self.logger.warning(order_log)
            return False
        while uuid and self.upbit.get_order(uuid).get('state') == 'wait':
            time.sleep(1)
        time.sleep(2)
        order_log = self.upbit.get_order(uuid)
        self.logger.debug(f"sell {order_log=}")

        coin.avg_sell_price = calculate_avg_sell_price(order_log.get('trades'))
        coin.sold_amount = calculate_total_amount(order_log)
        self.logger.info(f'매수가: {coin.avg_buy_price}, 매도가: {coin.avg_sell_price}, '
                         f'수익률: {calculate_rate(coin.avg_sell_price, coin.avg_buy_price)}')
        self.discord_conn.post(self.discord_conn.sell_data(coin))
        coin.status = status
        coin.dca_buy_cnt = 0
        coin.bought_amount = 0
        coin.avg_buy_price = 0
        coin.buy_volume_cnt = 0
        coin.avg_sell_price = 0
        coin.sold_amount = 0
        self.hold_krw = float(self.get_balance_info()['balance'])
        return True

    def update_current_infos(self, coins: list[Coin]):
        if len(coins) >= 100:
            current_price = pyupbit.get_current_price(['KRW-' + coin.name for coin in coins[:100]])
            current_price.update(pyupbit.get_current_price(['KRW-' + coin.name for coin in coins[100:]]))
        else:
            current_price = pyupbit.get_current_price(['KRW-' + coin.name for coin in coins])
        for coin in coins:
            coin.current_volume = pyupbit.get_ohlcv("KRW-" + coin.name, interval='day', count=1).get("volume")[0]
            coin.current_price = current_price['KRW-' + coin.name]
            coin.low_price = min(coin.current_price, coin.low_price if coin.low_price != 0 else coin.current_price)
            coin.high_price = max(coin.current_price, coin.high_price if coin.high_price != 0 else coin.current_price)

    def update_last_infos(self, coins: list[Coin]):
        for coin in coins:
            ohlcv = pyupbit.get_ohlcv("KRW-" + coin.name, interval='day', count=2)
            coin.last_volume = ohlcv.get("volume")[0]
            coin.svb_info.max = ohlcv.get("high")[0]
            coin.svb_info.min = ohlcv.get("low")[0]
            coin.open_price = ohlcv.get("open")[1]

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

    def set_min_max_one(self, coin: Coin):
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

    def make_obj_list(self, names) -> list:
        return [Coin(name) for name in names]

    def add_bought_stock_info(self, coin_list):
        # TODO 내 계좌에 없고 pickle에만 남아있는 코인 초기화
        my_stocks_info = self.get_balances()
        for my_stock_info in my_stocks_info:
            if my_stock_info['currency'] == 'KRW':
                continue
            for coin in coin_list:
                if coin.name == my_stock_info['currency']:
                    coin.status = Status.BOUGHT
                    coin.avg_buy_price = float(my_stock_info['avg_buy_price'])
                    coin.buy_volume_cnt = float(my_stock_info['balance'])
                    if coin.dca_buy_cnt == 0:
                        coin.dca_buy_cnt = 1
                    break
            else:
                self.logger.warning(f"{my_stock_info['currency']}을 coin_list에서 찾을 수 없습니다.")

    def sell_all(self, stocks_list):
        for stock in stocks_list:
            if stock.status == Status.BOUGHT:
                self.sell(stock, self.get_balance(stock.name))


def setup_status_wait(stocks_list: list[Coin]):
    for stock in stocks_list:
        stock.status = Status.WAIT
        stock.low_price = 0


if __name__ == "__main__":
    conn = CoinTradingConnector()
    order = conn.get_order("ae428351-7785-45e3-9905-f4dc19feeaf7")
    print(type(order.get('created_at')))
    print((order.get('created_at')))
    print(datetime.strptime(order.get('created_at')[:-6], "%Y-%m-%dT%H:%M:%S"))
    a = datetime.now()
    time.sleep(5)
    print(datetime.now() - a)
    exit()
    watching_list2 = conn.get_watching_list()
    obj_list = conn.make_obj_list(watching_list2)
    conn.add_bought_stock_info(obj_list)
    # for obj in obj_list:
    #     print(obj.name, obj.status)
    # conn.buy(Coin("XRP"), 5050)
    # conn.sell(Coin("XRP"), 3.44709897)
    # print(float(conn.get_balance_info("XEC").get('avg_buy_price')))
    # exit()
    print(conn.get_balance_info('BTT'))
    print(conn.get_balance_info('DAWN'))
    print(conn.get_balance_info('XRP'))
    print(conn.upbit.get_order('ae428351-7785-45e3-9905-f4dc19feeaf7'))
    print(conn.upbit.get_order('40faa4e2-28cd-49ba-8d98-05b220c01965'))
    print(conn.upbit.get_order('06e65ae2-a98a-4ae3-a65a-b171f7cb9fba'))
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
# {'uuid': '06e65ae2-a98a-4ae3-a65a-b171f7cb9fba', 'side': 'ask', 'ord_type': 'market', 'price': None, 'state': 'wait', 'market': 'KRW-STRAX', 'created_at': '2021-11-17T22:10:56+09:00', 'volume': '40.55972682', 'remaining_volume': '40.55972682', 'reserved_fee': '0.0', 'remaining_fee': '0.0', 'paid_fee': '0.0', 'locked': '40.55972682', 'executed_volume': '0.0', 'trades_count': 0}
# {'uuid': '06e65ae2-a98a-4ae3-a65a-b171f7cb9fba', 'side': 'ask', 'ord_type': 'market', 'price': None, 'state': 'done', 'market': 'KRW-STRAX', 'created_at': '2021-11-17T22:10:56+09:00', 'volume': '40.55972682', 'remaining_volume': '0.0', 'reserved_fee': '0.0', 'remaining_fee': '0.0', 'paid_fee': '59.0144025231', 'locked': '0.0', 'executed_volume': '40.55972682', 'trades_count': 1, 'trades': [{'market': 'KRW-STRAX', 'uuid': '9179e650-dcdb-47cc-89bd-1eeb6cb384b2', 'price': '2910.0', 'volume': '40.55972682', 'funds': '118028.8050462', 'created_at': '2021-11-17T22:10:56+09:00', 'side': 'ask'}]}
def test_daily_at_9():
    a = CoinTradingConnector()
    stocks_name = a.get_watching_list()
    stocks_list = a.make_obj_list(stocks_name)
    print()
    a.daily_at_9(stocks_list)


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
        a.heartbeat_url()
        time.sleep(3)


def test_heartbeat():
    a = 1 * 60
    print(a)
    for _ in range(100):
        b = datetime.datetime.now().timestamp()
        print(datetime.datetime.now(), b - b % a)
        time.sleep(1)


def test_get_balance():
    a = CoinTradingConnector()
    print()
    print(a.get_balance("APENFT"))
    print(type(a.get_balance("APENFT")))


def test_get_balance_info():
    a = CoinTradingConnector()
    print(a.get_balance_info()['balance'])
    print(type(a.get_balance_info()['balance']))


def test_get_ohlcv():
    a = CoinTradingConnector()
    print()
    b = pyupbit.get_ohlcv("KRW-BTC", interval='day', count=2)
    print(b)
    print(b.get("volume")[0])
    print(b.get("high")[0])
    print(b.get("low")[0])
    print(b.get("open")[1])  # 금일 시가
    print()


def test_update_current_infos():
    a = CoinTradingConnector()
    print()

    assert False


def test_buy_limit_order():
    assert False
