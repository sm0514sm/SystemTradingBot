import time
from datetime import date

from object.Coin import Coin, CmmStatus
from strategy_type.AbstractStrategy import AbstractStrategy
from util.Calculator import calculate_rate
from util.MethodLoggerDecorator import method_logger_decorator


class CatchMinMax(AbstractStrategy):
    @method_logger_decorator
    def run_strategy(self):
        last_date = date.today()
        stocks_name: list[str] = self.connector.get_watching_list()
        stocks_list: list[Coin] = self.connector.make_obj_list(stocks_name)
        self.logger.info(f'{len(stocks_name)}개의 종목 확인')
        self.connector.apply_pickles(stocks_list, "CMM")
        self.connector.set_min_max(stocks_list)
        self.connector.add_bought_stock_info(stocks_list)
        while True:
            self.connector.heartbeat()
            self.connector.save_pickles(stocks_list, "CMM")
            time.sleep(5)
            if last_date != date.today():
                last_date = date.today()
                self.logger.info("날짜가 바뀌어 최소값과 최대값을 다시 계산합니다.")
                self.connector.set_min_max(stocks_list)
            self.connector.set_current_prices(stocks_list)
            for stock in stocks_list:
                self.logger.debug(stock)
                if stock.target_buy_price == 0:
                    stock.target_buy_price = stock.cmm_info.min
                if stock.status in [CmmStatus.WAIT, CmmStatus.BOUGHT] and stock.current_price <= stock.target_buy_price\
                        and self.connector.get_balance() >= self.connector.cmm_config['buy_amount']:
                    if self.connector.buy(stock, self.connector.cmm_config['buy_amount']):
                        stock.status = CmmStatus.BOUGHT
                        stock.target_buy_price *= (100 - int(self.connector.cmm_config['dca_buy_rate'])) / 100
                        stock.avg_buy_price = stock.avg_buy_price
                        if stock.dca_buy_cnt >= int(self.connector.cmm_config['max_dca_buy_cnt']):
                            stock.status = CmmStatus.END_BUY
                elif stock.status in [CmmStatus.BOUGHT, CmmStatus.END_BUY] \
                        and (stock.current_price >= stock.cmm_info.max
                             or calculate_rate(stock.current_price, stock.avg_buy_price)
                             >= int(self.connector.cmm_config['profit_rate'])):
                    stock.status = CmmStatus.SELL_READY
                    if self.connector.sell(stock, stock.buy_volume_cnt):
                        stock.status = CmmStatus.WAIT
                        stock.avg_sell_price = stock.current_price
            self.logger.debug("-" * 100)