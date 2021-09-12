from strategy_type.AbstractStrategy import AbstractStrategy
from util.MethodLoggerDecorator import MethodLoggerDecorator


class CatchMinMax(AbstractStrategy):
    @MethodLoggerDecorator
    def run_strategy(self):
        # 종목들의 기간 중 최소, 최대값 가져오기
        # stock_dict = self.connector.get_min_max(종목명들)
        # 이미 가지고 있는 코인 정보 추가
        # while True:
        #   if 날짜가 바뀌면:
        #       최소, 최댓값 갱신
        # for stock, current_price in self.connector.get_current_prices(종목명들):
        #   self.logger.log()
        #   if stock_dict[stock].status == Status.WAIT and current_price < stock_dict[stock].min \
        #           and self.connector.get_balance() >= BUY_AMOUNT:
        #       stock_dict[stock].status = Status.BUY_READY
        # elif stock_dict[stock].status == Status.BUY_READY:
        #   stock_dict[stock].min = min(stock_dict[stock].min, current_price)
        #   stock_dict[stock].target_buy_price = stock_dict[stock].min * (1 + VALUE_K)
        #   if current_price > stock_dict[stock].target_buy_price:
        #       print(self.connector.buy(stock, BUY_AMOUNT))
        #       time.sleep(1)
        #       stock_dict[stock].status = Status.BOUGHT
        #       stock_dict[stock].avg_buy_price = float(self.connector.get_avg_buy_price(stock[4:]))
        # elif stock_dict[stock].status == Status.BOUGHT \
        #      and (current_price > stock_dict[stock].max
        #           or calculate_rate(current_price, stock_dict[stock].avg_buy_price) >= PROFIT_RATE):
        #   stock_dict[stock].status = Status.SELL_READY
        # elif stock_dict[stock].status == Status.SELL_READY:
        #     stock_dict[stock].max = max(stock_dict[stock].max, current_price)
        #     stock_dict[stock].target_sell_price = stock_dict[stock].max * (1 - VALUE_K)
        #     print(f"{stock_dict[stock].target_sell_price:.1f}", end=" ")
        #     if current_price < stock_dict[stock].target_sell_price \
        #             or calculate_rate(current_price, stock_dict[stock].avg_buy_price) >= PROFIT_RATE:
        #         print(self.connector.sell(stock, self.connector.get_balance(stock[4:])))
        #         stock_dict[stock].status = Status.WAIT
        #         stock_dict[stock].avg_sell_price = current_price
        #         print(f"{stock_dict[stock].avg_buy_price} -> {stock_dict[stock].avg_sell_price}"
        #               f"({calculate_rate(stock_dict[stock].avg_sell_price, stock_dict[stock].avg_buy_price)})")
        #         stock_dict[stock] = stock(stock_dict[stock].min, stock_dict[stock].max)  # 초기화
        pass
