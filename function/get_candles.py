import requests
import json
import datetime
import time


def get_candles(market: str, count: int, sleep: float = 0.0, minute: int = 1) -> list:
    try:
        time.sleep(sleep)
        url = f"https://api.upbit.com/v1/candles/minutes/{minute}"

        querystring = {"market": market, "count": count}

        response = requests.request("GET", url, params=querystring)
        # print(response)
        # print(json.dumps(response.json(), indent=2))
        res_list: list = response.json()
        return res_list
    except (json.decoder.JSONDecodeError, requests.exceptions.ConnectionError) as e:
        time.sleep(sleep)
        return get_candles(market, count, sleep, minute)


if __name__ == "__main__":
    while True:
        test = get_candles("KRW-BTC", 5, minute=5)
        print(test[0])
        print(test[1])
        a = datetime.datetime.strptime(test[0]['candle_date_time_kst'], '%Y-%m-%dT%H:%M:%S')
        print(a)
        b = datetime.datetime.fromtimestamp(test[0]['timestamp'] / 1000)
        print(b)
        print((b - a).total_seconds())

'''
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
