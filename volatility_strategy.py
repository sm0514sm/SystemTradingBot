import os
from Coin import Coin, State
from function.get_candles import get_candles
from function.get_now_time import get_now_time
from function.order_stock import *
from function.print_your_config import print_order_config
from function.get_market_code import get_market_code
from datetime import datetime


config = configparser.ConfigParser()
config.read('config.ini', encoding='UTF8')

VM_order_config = config['VB_ORDER']
candle_type: str = VM_order_config.get('CANDLE_TYPE')
unit: int = VM_order_config.getint('MINUTE_CANDLE_UNIT')
percent_buy_range: int = VM_order_config.getint('PERCENT_OF_BUY_RANGE')
percent_of_buying: int = VM_order_config.getint('PERCENTS_OF_BUYING')  # 추가예
percent_of_stop_loss: float = VM_order_config.getfloat('PERCENT_OF_STOP_LOSS')
percent_of_add_buy: float = VM_order_config.getfloat('PERCENT_OF_ADD_BUY')
sell_add_buy_time: float = VM_order_config.getfloat('SELL_ADD_BUY_TIME')

coin_div_cnt: int = VM_order_config.getint('COIN_DIV_CNT')
coin_div_select: int = VM_order_config.getint('COIN_DIV_SELECT')
coin_maximum: int = VM_order_config.getint('COIN_MAXIMUM')


def volatility_strategy(coins_name: list):
    os.makedirs('logs', exist_ok=True)
    log_file = open("logs/VB_order.log", "a")

    print_order_config(config.items(section="VB_ORDER"))
    coin_dict = dict()
    for coin_name in coins_name:
        coin_dict[coin_name] = Coin(coin_name)
    while True:
        for i, coin in enumerate(coin_dict.values()):
            candles = get_candles('KRW-' + coin.coin_name, count=2, minute=unit, candle_type=candle_type)
            coin.high_price = max(candles[0]["trade_price"], coin.high_price)
            now = candles[0]['candle_date_time_kst']

            if coin.state in [State.BOUGHT, State.ADDBUY]:
                coin.earnings_ratio = (candles[0]["trade_price"] - coin.avg_buy_price) / candles[0]["trade_price"] * 100
                coin.max_earnings_ratio = max(coin.earnings_ratio, coin.max_earnings_ratio)
            if coin.state == State.WAIT:
                print(f'{get_now_time()} {coin.coin_name:>5}({set_state_color(coin.state)})| '
                      f'목표 가: {coin.buy_price:>11.2f}, 현재 가: {candles[0]["trade_price"]:>10}'
                      f' ({set_dif_color(candles[0]["trade_price"], coin.buy_price)}) '
                      f'최대 {coin.max_earnings_ratio:>6.2f} %')
            elif coin.state in [State.BOUGHT, State.ADDBUY]:
                print(f'{get_now_time()} {coin.coin_name:>5}({set_state_color(coin.state)})| '
                      f'구매 가: {coin.avg_buy_price:>11.2f}, 현재 가: {candles[0]["trade_price"]:>10}'
                      f' ({set_dif_color(candles[0]["trade_price"], coin.avg_buy_price)}) '
                      f'최대 {coin.max_earnings_ratio:6.2f} %')

            # 추가 매수
            if coin.state == State.BOUGHT and coin.earnings_ratio >= percent_of_add_buy:
                # 매수
                buy_result = coin.buy_coin(price=294000, addbuy=True)
                if not buy_result:
                    continue
                print(f'\033[101m{get_now_time()} {coin.coin_name:>5}(ADDBUY)| {coin.bought_amount}원\033[0m')
                log_file.write(f'{get_now_time()}, {coin.coin_name}, ADDBUY, {coin.bought_amount}\n')
                coin.earnings_ratio = (candles[0]["trade_price"] - coin.avg_buy_price) / candles[0]["trade_price"] * 100
                coin.max_earnings_ratio = 0

            # 매도 조건
            # 1. 시간 캔들이 바뀐 경우
            # 2. 구매한 상태이고 수익률이 손실 기준보다 현재가격이 낮은 경우
            # 3. 현재 캔들의 고가에서 기준이상 떨어진 경우
            if coin.check_time != now \
                    or (coin.state in [State.BOUGHT, State.ADDBUY]
                        and coin.earnings_ratio < max_drop_rule(coin.max_earnings_ratio)):
                print(f'1. time_change: {coin.check_time != now} '
                      f'2. is_buy: {coin.state in [State.BOUGHT, State.ADDBUY]} '
                      f'3. ratio_drop: {coin.earnings_ratio < max_drop_rule(coin.max_earnings_ratio)} '
                      f'({coin.earnings_ratio} < {max_drop_rule(coin.max_earnings_ratio)})')
                if coin.check_time != now and i == 0:
                    print(f'----------------------------------- UPDATE ---------------------------------------'
                          f'\n{coin.check_time} -> \033[36m{now}\033[0m')
                if coin.state in [State.BOUGHT, State.ADDBUY]:
                    sell_result = coin.sell_coin()
                    print(f'\033[104m{get_now_time()} {coin.coin_name:>5}(  SELL)| {int(round(get_sell_price(sell_result)))}원\033[0m')
                    log_file.write(f'{get_now_time()}, {coin.coin_name}, SELL, {int(round(get_sell_price(sell_result)))}\n')
                if coin.check_time != now:
                    coin.state = State.WAIT
                    coin.max_earnings_ratio = 0
                    coin.earnings_ratio = 0
                if coin.check_time != now and i == len(coin_dict) - 1:
                    print(f'---------------------------------------------------------------------------------')
                coin.check_time = now
                coin.variability = candles[1]['high_price'] - candles[1]['low_price']
                coin.buy_price = candles[0]["opening_price"] + coin.variability * (percent_buy_range / 100)
                coin.high_price = candles[0]["opening_price"]
            else:  # 시간이 동일하다면
                if coin.state != State.WAIT:
                    continue
                if coin.variability == 0 or candles[0]['trade_price'] < coin.buy_price:
                    continue

                # 매수
                buy_result = coin.buy_coin(price=6000)
                if not buy_result:
                    continue
                print(f'\033[101m{get_now_time()} {coin.coin_name:>5}(   BUY)| {coin.bought_amount}원\033[0m')
                log_file.write(f'{get_now_time()}, {coin.coin_name}, BUY, {coin.bought_amount}\n')


# 최대 수익률 대비 몇 % 떨어지면 팔지 계산
def max_drop_rule(max_earnings_ratio):
    if max_earnings_ratio < 5:
        return percent_of_stop_loss
    return max_earnings_ratio - max_earnings_ratio // 5


def set_state_color(state) -> str:
    if state == State.BOUGHT:
        return f'\033[91m{state.name:>6}\033[0m'
    elif state == State.ADDBUY:
        return f'\033[96m{state.name:>6}\033[0m'
    else:
        return f'{state.name:>6}'


def set_dif_color(a, b) -> str:
    value = (a - b) / a * 100
    if value < 0:
        return f'\033[34m{value:>6.2f}%\033[0m'
    else:
        return f'\033[31m{value:>6.2f}%\033[0m'


if __name__ == '__main__':
    volatility_strategy(get_market_code(div_cnt=coin_div_cnt, maximum=coin_maximum)[coin_div_select])
