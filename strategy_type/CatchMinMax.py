import time
from datetime import date

from object.Coin import Coin, Status
from strategy_type.AbstractStrategy import AbstractStrategy
from util.Calculator import calculate_rate
from util.MethodLoggerDecorator import method_logger_decorator


class CatchMinMax(AbstractStrategy):
    @method_logger_decorator
    def run_strategy(self):
        multiple_amount, start_amount = self.get_amount()
        stocks_list = self.connector.apply_pickles(self.stocks_list, "CMM")
        # stocks_list = list(map(limit_new_stock, map(limit_small_price, stocks_list)))

        self.logger.info(f'{len(self.stocks_name)}개의 종목 확인')
        self.connector.set_min_max(stocks_list)
        self.connector.add_bought_stock_info(stocks_list)
        while True:
            self.connector.heartbeat()
            self.connector.daily_at_9()
            self.connector.save_pickles(stocks_list, "CMM")
            time.sleep(15)
            if self.last_date != date.today():
                self.last_date = date.today()
                self.logger.info("날짜가 바뀌어 최소값과 최대값을 다시 계산합니다.")
                self.connector.set_min_max(stocks_list)
            self.connector.update_current_infos(stocks_list)

            for stock in stocks_list:
                self.coin_logger.info(stock)
                if stock.target_buy_price == 0:
                    stock.target_buy_price = stock.cmm_info.min
                if stock.status in [Status.WAIT, Status.BOUGHT] and stock.current_price <= stock.target_buy_price:
                    if self.connector.hold_krw < stock.get_next_buy_amount(start_amount, multiple_amount):
                        stock.target_buy_price *= (100 - self.connector.cmm_config['dca_buy_rate']) / 100
                        continue
                    if self.connector.buy(stock, stock.get_next_buy_amount(start_amount, multiple_amount)):
                        stock.status = Status.BOUGHT
                        stock.target_buy_price *= (100 - self.connector.cmm_config['dca_buy_rate']) / 100
                        self.connector.discord_conn.post(self.connector.discord_conn.buy_data(stock))
                        if stock.dca_buy_cnt >= self.connector.cmm_config['max_dca_buy_cnt']:
                            stock.status = Status.END_BUY
                elif stock.status in [Status.BOUGHT, Status.END_BUY] \
                        and (stock.current_price >= stock.cmm_info.max
                             or calculate_rate(stock.current_price, stock.avg_buy_price)
                             >= self.connector.cmm_config['profit_rate']):
                    stock.status = Status.SELL_READY
                    if self.connector.sell(stock, stock.buy_volume_cnt, Status.WAIT):
                        stock.status = Status.WAIT
                        stock.avg_sell_price = stock.current_price
                        self.connector.set_min_max_one(stock)
                        stock.target_buy_price = stock.cmm_info.min
            self.logger.debug("-" * 100)

    def get_amount(self):
        start_amount = self.connector.cmm_config['start_amount']
        multiple_amount = self.connector.cmm_config['multiple_amount']
        return multiple_amount, start_amount
