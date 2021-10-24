from object.Coin import Coin, CmmStatus
from strategy_type.AbstractStrategy import AbstractStrategy
from util.MethodLoggerDecorator import MethodLoggerDecorator, method_logger_decorator
from datetime import datetime, date


class CatchMinMax(AbstractStrategy):
    @method_logger_decorator
    def run_strategy(self):
        last_date = date.today()
        stocks_name: list = self.connector.get_watching_list()
        stocks_list: list = self.connector.make_obj_list(stocks_name)
        self.connector.set_min_max(stocks_list)
        self.connector.add_bought_stock_info(stocks_list)
        while True:
            if last_date != date.today():
                last_date = date.today()
                self.logger.info("날짜가 바뀌어 최소값과 최대값을 다시 계산합니다.")
                self.connector.set_min_max(stocks_list)
            self.connector.set_current_prices(stocks_list)
            for stock in stocks_list:
                self.logger.debug(stock)
                if stock.status == CmmStatus.WAIT and stock.current_price < stock.cmm_info.min \
                        and self.connector.get_balance() >= 100000:
                    self.connector.buy() # TODO 설정 필요
                    stock.status = CmmStatus.BOUGHT
                elif stock.status == CmmStatus.BUY_READY:
                    stock.cmm_info.min = min(stock.cmm_info.min, stock.current_price)
        #      stock_dict[stock].target_buy_price = stock_dict[stock].min * (1 + VALUE_K)
        #      if current_price > stock_dict[stock].target_buy_price:
        #          print(self.connector.buy(stock, BUY_AMOUNT))
        #          time.sleep(1)
        #          stock_dict[stock].status = Status.BOUGHT
        #          stock_dict[stock].avg_buy_price = float(self.connector.get_avg_buy_price(stock[4:]))
        #    elif stock_dict[stock].status == Status.BOUGHT \
        #         and (current_price > stock_dict[stock].max
        #              or calculate_rate(current_price, stock_dict[stock].avg_buy_price) >= PROFIT_RATE):
        #      stock_dict[stock].status = Status.SELL_READY
        #    elif stock_dict[stock].status == Status.SELL_READY:
        #        stock_dict[stock].max = max(stock_dict[stock].max, current_price)
        #        stock_dict[stock].target_sell_price = stock_dict[stock].max * (1 - VALUE_K)
        #        print(f"{stock_dict[stock].target_sell_price:.1f}", end=" ")
        #        if current_price < stock_dict[stock].target_sell_price \
        #                or calculate_rate(current_price, stock_dict[stock].avg_buy_price) >= PROFIT_RATE:
        #            print(self.connector.sell(stock, self.connector.get_balance(stock[4:])))
        #            stock_dict[stock].status = Status.WAIT
        #            stock_dict[stock].avg_sell_price = current_price
        #            print(f"{stock_dict[stock].avg_buy_price} -> {stock_dict[stock].avg_sell_price}"
        #                  f"({calculate_rate(stock_dict[stock].avg_sell_price, stock_dict[stock].avg_buy_price)})")
        #            stock_dict[stock] = stock(stock_dict[stock].min, stock_dict[stock].max)  # 초기화
