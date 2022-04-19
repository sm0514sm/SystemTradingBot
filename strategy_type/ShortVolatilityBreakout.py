import time
from datetime import date

from object.Coin import Status, Coin
from strategy_type.AbstractStrategy import AbstractStrategy
from util.Calculator import calculate_rate
from util.MethodLoggerDecorator import method_logger_decorator


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
        if stock.current_volume < stock.last_volume:
            stock.status = Status.PASS
            return
            # TODO: 지정가 구매
        # self.connector.buy_limit(stock, 구매가, 개수)
        self.connector.buy(stock, 6000)
        setup_target_sell_price(stock)

    def do_check_buy_success(self, stock: Coin):
        """매수 예약 걸어놓은 stock이 매수가 성공했는지 확인"""
        # TODO: 테스트 기간에는 시장가 매수해서 스킵
        pass

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


def setup_target_sell_price(coin: Coin):
    coin.target_profit_cut_sell_price = coin.avg_buy_price * (1 + 0.01)
    coin.target_loss_cut_sell_price = coin.avg_buy_price * (1 - 0.01)
    return coin
