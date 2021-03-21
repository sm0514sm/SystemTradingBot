import os
from Coin import Coin, State
from function.get_candles import get_candles
from function.get_now_time import get_now_time
from function.order_stock import *
from function.print_your_config import print_order_config


config = configparser.ConfigParser()
config.read('config.ini', encoding='UTF8')

VM_order_config = config['VB_ORDER']
candle_type: str = VM_order_config.get('CANDLE_TYPE')
unit: int = VM_order_config.getint('MINUTE_CANDLE_UNIT')
percent_buy_range: int = VM_order_config.getint('PERCENT_OF_BUY_RANGE')
percent_of_buying: int = VM_order_config.getint('PERCENTS_OF_BUYING')  # 추가예
percent_of_stop_loss: float = VM_order_config.getfloat('PERCENT_OF_STOP_LOSS')


def volatility_strategy(coins_name: list):
    print_order_config(config.items(section="VB_ORDER"))
    coin_dict = dict()
    for coin_name in coins_name:
        coin_dict[coin_name] = Coin(coin_name)
    while True:
        for i, coin in enumerate(coin_dict.values()):
            candles = get_candles('KRW-' + coin.coin_name, count=2, minute=unit, candle_type=candle_type)
            coin.high_price = max(candles[0]["trade_price"], coin.high_price)
            now = candles[0]['candle_date_time_kst']
            if coin.state == State.WAIT:
                print(f'{get_now_time()} {coin.coin_name:>5}({set_state_color(coin.state)})| '
                      f'목표 가: {coin.buy_price:>11.2f}, 현재 가: {candles[0]["trade_price"]:>10}'
                      f' ({set_dif_color(candles[0]["trade_price"], coin.buy_price)})')
            elif coin.state == State.BOUGHT:
                print(f'{get_now_time()} {coin.coin_name:>5}({set_state_color(coin.state)})| '
                      f'구매 가: {coin.avg_buy_price:>11.2f}, 현재 가: {candles[0]["trade_price"]:>10}'
                      f' ({set_dif_color(candles[0]["trade_price"], coin.avg_buy_price)})')
            percent_dif = (candles[0]["trade_price"] - coin.avg_buy_price) / candles[0]["trade_price"] * 100

            # 매도 조건
            # 1. 시간 캔들이 바뀐 경우
            # 2. 손실 기준보다 현재가격이 낮은 경우
            # 3. TODO 현재 캔들의 고가에서 기준이상 떨어진 경우
            if coin.check_time != now or (coin.state == State.BOUGHT and percent_dif < percent_of_stop_loss):
                if coin.check_time != now and i == 0:
                    print(f'----------------------------------- UPDATE ---------------------------------------'
                          f'\n{coin.check_time} -> \033[36m{now}\033[0m')
                if coin.state == State.BOUGHT:
                    sell_result = coin.sell_coin()
                    if sell_result == "Not bought" or not sell_result:
                        print(f'\033[100m{get_now_time()} {coin.coin_name:>5}( ERROR)|\033[0m')
                    else:
                        print(f'\033[104m{get_now_time()} {coin.coin_name:>5}(  SELL)| '
                              f'{round(get_total_sell_price(sell_result))}\033[0m')
                        with open("logs/VB_order.log", "a") as f:
                            f.write(f'{get_now_time()} {coin.coin_name:>5}(  SELL)| '
                                    f'{round(get_total_sell_price(sell_result))}원\n')
                if coin.check_time != now and i == len(coin_dict) - 1:
                    print(f'---------------------------------------------------------------------------------')
                coin.check_time = now
                coin.variability = candles[1]['high_price'] - candles[1]['low_price']
                coin.buy_price = candles[0]["opening_price"] + coin.variability * (percent_buy_range / 100)
                coin.high_price = candles[0]["opening_price"]
            else:  # 시간이 동일하다면
                if coin.state == State.BOUGHT:
                    continue
                if coin.variability == 0 or candles[0]['trade_price'] < coin.buy_price:
                    continue

                # 매수
                buy_result = coin.buy_coin(price=10000)
                if not buy_result:
                    continue
                print(f'\033[101m{get_now_time()} {coin.coin_name:>5}(   BUY)| '
                      f'{coin.bought_amount}원\033[0m')
                os.makedirs('logs', exist_ok=True)
                with open("logs/VB_order.log", "a") as f:
                    f.write(f'{get_now_time()} {coin.coin_name:>5}(   BUY)| '
                            f'{coin.bought_amount}원\n')


def set_state_color(state) -> str:
    if state == State.BOUGHT:
        return f'\033[91m{state.name:>6}\033[0m'
    else:
        return f'{state.name:>6}'


def set_dif_color(a, b) -> str:
    value = (a - b) / a * 100
    if value < 0:
        return f'\033[34m{value:>6.2f}%\033[0m'
    else:
        return f'\033[31m{value:>6.2f}%\033[0m'


if __name__ == '__main__':
    volatility_strategy(
        ['BTC', 'ETH', 'NEO', 'MTL', 'LTC', 'XRP', 'ETC', 'OMG', 'SNT', 'WAVES', 'XEM', 'QTUM', 'LSK', 'STEEM', 'XLM',
         'ARDR', 'KMD', 'ARK', 'STORJ', 'GRS', 'REP', 'EMC2', 'ADA', 'SBD', 'POWR', 'BTG', 'ICX', 'EOS', 'TRX', 'SC',
         'IGNIS', 'ONT', 'ZIL', 'POLY', 'ZRX', 'SRN', 'LOOM', 'BCH', 'ADX', 'BAT', 'IOST', 'DMT', 'RFR', 'CVC', 'IQ',
         'IOTA', 'MFT', 'ONG', 'GAS', 'UPP', 'ELF', 'KNC', 'BSV', 'THETA', 'EDR', 'QKC', 'BTT', 'MOC', 'ENJ', 'TFUEL',
         'MANA', 'ANKR', 'NPXS', 'AERGO', 'ATOM', 'TT', 'CRE', 'SOLVE', 'MBL', 'TSHP', 'WAXP', 'HBAR', 'MED', 'MLK',
         'STPT', 'ORBS', 'VET', 'CHZ', 'PXL', 'STMX', 'DKA', 'HIVE', 'KAVA', 'AHT', 'SPND', 'LINK', 'XTZ', 'BORA',
         'JST', 'CRO', 'TON', 'SXP', 'LAMB', 'HUNT', 'MARO', 'PLA', 'DOT', 'SRM', 'MVL', 'PCI', 'STRAX', 'AQT', 'BCHA',
         'GLM', 'QTCON', 'SSX', 'META', 'OBSR', 'FCT2', 'LBC', 'CBK', 'SAND', 'HUM', 'DOGE']
    )

'''
['BTC', 'ETH', 'NEO', 'MTL', 'LTC', 'XRP', 'ETC', 'OMG', 'SNT', 'WAVES', 'XEM', 'QTUM', 'LSK', 'STEEM', 'XLM',
         'ARDR', 'KMD', 'ARK', 'STORJ', 'GRS', 'REP', 'EMC2', 'ADA', 'SBD', 'POWR', 'BTG', 'ICX', 'EOS', 'TRX', 'SC',
         'IGNIS', 'ONT', 'ZIL', 'POLY', 'ZRX', 'SRN', 'LOOM', 'BCH', 'ADX', 'BAT', 'IOST', 'DMT', 'RFR', 'CVC', 'IQ',
         'IOTA', 'MFT', 'ONG', 'GAS', 'UPP', 'ELF', 'KNC', 'BSV', 'THETA', 'EDR', 'QKC', 'BTT', 'MOC', 'ENJ', 'TFUEL',
         'MANA', 'ANKR', 'NPXS', 'AERGO', 'ATOM', 'TT', 'CRE', 'SOLVE', 'MBL', 'TSHP', 'WAXP', 'HBAR', 'MED', 'MLK',
         'STPT', 'ORBS', 'VET', 'CHZ', 'PXL', 'STMX', 'DKA', 'HIVE', 'KAVA', 'AHT', 'SPND', 'LINK', 'XTZ', 'BORA',
         'JST', 'CRO', 'TON', 'SXP', 'LAMB', 'HUNT', 'MARO', 'PLA', 'DOT', 'SRM', 'MVL', 'PCI', 'STRAX', 'AQT', 'BCHA',
         'GLM', 'QTCON', 'SSX', 'META', 'OBSR', 'FCT2', 'LBC', 'CBK', 'SAND', 'HUM', 'DOGE']

'''
