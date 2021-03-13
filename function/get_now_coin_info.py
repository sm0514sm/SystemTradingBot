import requests
import json
import time


def get_now_coin_info(market: str, sleep: float = 0):
    time.sleep(sleep)
    url = "https://api.upbit.com/v1/ticker"
    querystring = {"markets": market}
    response = requests.request("GET", url, params=querystring)

    # print(json.dumps(response.json(), indent=2))

    return response.json()[0]


if __name__ == '__main__':
    while True:
        try:
            print(get_now_coin_info(f"KRW-BTC", sleep=0.5))
        except json.decoder.JSONDecodeError:
            pass

# {'market': 'KRW-BTC', 'candle_date_time_utc': '2021-03-13T11:30:00', 'candle_date_time_kst': '2021-03-13T20:30:00', 'opening_price': 69360000.0, 'high_price': 69360000.0, 'low_price': 69147000.0, 'trade_price': 69201000.0, 'timestamp': 1615635216369, 'candle_acc_trade_price': 6385707863.41599, 'candle_acc_trade_volume': 92.22191557, 'unit': 5}
# {'market': 'KRW-BTC', 'trade_date': '20210313', 'trade_time': '113552', 'trade_date_kst': '20210313', 'trade_time_kst': '203552', 'trade_timestamp': 1615635352000, 'opening_price': 66607000.0, 'high_price': 69788000.0, 'low_price': 65416000.0, 'trade_price': 69302000.0, 'prev_closing_price': 66607000.0, 'change': 'RISE', 'change_price': 2695000.0, 'change_rate': 0.0404612128, 'signed_change_price': 2695000.0, 'signed_change_rate': 0.0404612128, 'trade_volume': 0.0048839, 'acc_trade_price': 464436658626.1546, 'acc_trade_price_24h': 742487068720.3325, 'acc_trade_volume': 6889.69252462, 'acc_trade_volume_24h': 11102.85541644, 'highest_52_week_price': 69788000.0, 'highest_52_week_date': '2021-03-13', 'lowest_52_week_price': 5489000.0, 'lowest_52_week_date': '2020-03-13', 'timestamp': 1615635352549}