import time

from object.Coin import Status, Coin
from strategy_type.AbstractStrategy import AbstractStrategy
from util.Calculator import calculate_rate
from util.MethodLoggerDecorator import method_logger_decorator
from datetime import datetime


class ShortVolatilityBreakout(AbstractStrategy):
    @method_logger_decorator
    def run_strategy(self):
        stocks_list: list[Coin] = self.connector.apply_pickles(self.stocks_list, "SVB")
        self.logger.info(f'{len(self.stocks_list)}개의 종목 확인')
        self.connector.add_bought_stock_info(stocks_list)

        while True:
            self.connector.heartbeat()
            self.connector.daily_at_9(stocks_list)
            self.connector.save_pickles(stocks_list, "SVB")
            time.sleep(5)
            self.connector.update_current_infos(stocks_list)
            stocks_list = list(map(self.setup_target_buy_price, stocks_list))

            for stock in stocks_list:
                self.coin_logger.info(stock)
                match stock.status:
                    case Status.WAIT:
                        self.do_try_buy(stock)
                    case Status.TRY_BUY:
                        self.do_check_buy_success(stock)
                    case Status.BOUGHT:
                        self.do_try_sell(stock)
                    case Status.TRY_SELL:
                        self.do_check_sell_success(stock)
                    case _:
                        pass

    def do_try_buy(self, stock: Coin):
        """구매 조건에 맞는 stock에 대해 매수 시도

        구매 조건
            1. stock의 현재가가 목표매수가보다 높아야함
            2. stock의 현재거래량이 목표거래량보다 높아야함
        매수 시도
        """
        if stock.current_price < stock.target_buy_price:
            return
        if stock.current_volume < stock.last_volume / 2:
            stock.status = Status.PASS
            return
        self.connector.buy_limit_order(stock,
                                       stock.current_price,
                                       self.connector.svb_config['buy_amount'] / stock.current_price)

    def do_check_buy_success(self, stock: Coin):
        """매수 예약 걸어놓은 stock이 매수가 성공했는지 확인"""
        order = self.connector.get_order(stock.buy_uuid)
        if order.get('state') == 'wait':
            created_at: datetime = datetime.strptime(order.get('created_at')[:-6], "%Y-%m-%dT%H:%M:%S")
            if (datetime.now() - created_at).seconds >= 3 * 60:
                stock.status = Status.PASS
                self.connector.cancel_order(stock.buy_uuid)
            return
        stock.status = Status.BOUGHT
        stock.bought_amount += float(order.get('price')) * float(order.get('volume'))
        stock.avg_buy_price = float(self.connector.get_balance_info(stock.name).get('avg_buy_price'))
        stock.buy_volume_cnt = float(self.connector.get_balance_info(stock.name).get('balance'))
        self.connector.hold_krw = float(self.connector.get_balance_info()['balance'])
        self.setup_target_sell_price(stock)

    def do_try_sell(self, stock: Coin):
        """매도 조건에 맞는 stock에 대해 매도 시도

        매도조건
            - stock의 현재가가 익절목표매도가보다 높아야함
            - stock의 현재가가 손절목표매도가보다 낮아야함
        """
        if stock.target_profit_cut_sell_price > stock.current_price > stock.target_loss_cut_sell_price:
            return
        self.connector.sell(stock, stock.buy_volume_cnt, Status.PASS)

    def do_check_sell_success(self, stock: Coin):
        """매도 예약 걸어놓은 stock이 매도가 성공했는지 확인"""
        # TODO: 테스트 기간에는 시장가 매도해서 스킵
        pass

    def setup_target_sell_price(self, coin: Coin):
        coin.target_profit_cut_sell_price = coin.avg_buy_price * (1 + self.connector.svb_config['profit_rate'] / 100)
        coin.target_loss_cut_sell_price = coin.avg_buy_price * (1 - self.connector.svb_config['profit_rate'] / 100)
        return coin

    def setup_target_buy_price(self, coin: Coin):
        if coin.low_price == 0:
            coin.low_price = coin.current_price
        coin.target_buy_price = coin.low_price * (1 + 0.03)
        # if calculate_rate(coin.target_buy_price, coin.open_price) <= 1.5:
        #     coin.target_buy_price = coin.open_price * 1.015
        return coin
