import requests
import json
import datetime
import time
from function.sm_util import *


def get_candles(market: str, count: int, sleep: float = 0.0, minute: int = 1, candle_type: str = "minutes") -> list:

    time.sleep(sleep)
    if candle_type == "days":
        minute = ""
    url = f"https://api.upbit.com/v1/candles/{candle_type}/{minute}"

    querystring = {"market": market, "count": count}
    res_list = []
    try:
        response = requests.request("GET", url, params=querystring)
        # print_sm(response)
        # print_sm(json.dumps(response.json(), indent=2))
        res_list: list = response.json()
        tes = res_list[0]
    except (json.decoder.JSONDecodeError, requests.exceptions.ConnectionError, KeyError) as e:
        print(res_list)
        print(e)
        time.sleep(sleep + 0.25)
        return get_candles(market, count, sleep, minute, candle_type)
    return res_list


if __name__ == "__main__":
    while True:
        test = get_candles("KRW-BTC", 5, 1, minute=5, candle_type="days")
        print(test[0])
        print(test[1])
        a = datetime.datetime.strptime(test[0]['candle_date_time_kst'], '%Y-%m-%dT%H:%M:%S')
        print(a)
        b = datetime.datetime.fromtimestamp(test[0]['timestamp'] / 1000)
        print(b)
        print((b - a).total_seconds())

'''
KRW-BTC 5 1 5 days
KRW-STORJ 2 0.0  minutes
  {
    "market": "KRW-BTC",
    "candle_date_time_utc": "2021-02-23T12:33:00",
    "candle_date_time_kst": "2021-02-23T21:33:00",
    "opening_price": 51631000.0,
    "high_price": 51705000.0,
    "low_price": 51387000.0,
    "trade_price": 51563000.0,
    "timestamp": 1614083640180,
    "candle_acc_trade_price": 2247899666.8482,
    "candle_acc_trade_volume": 43.6014455,
    "unit": 1
  }
'''
