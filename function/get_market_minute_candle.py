import requests
import json
import datetime
import time


def get_market_minute_candle(market: str, count: int) -> list:
    try:
        url = "https://api.upbit.com/v1/candles/minutes/1"

        querystring = {"market": market, "count": count}

        response = requests.request("GET", url, params=querystring)
        # print(response.headers)
        # print(json.dumps(response.json(), indent=2))
        res_list: list = response.json()
        # print(res_list)
        return res_list
    except (json.decoder.JSONDecodeError, requests.exceptions.ConnectionError) as e:
        print("[ERROR]", e, market, count)
        pass
    # print(datetime.datetime.fromtimestamp(dict(res_list[0])['timestamp'] / 1000))
    # print(datetime.datetime.fromtimestamp(dict(res_list[1])['timestamp'] / 1000))
    # print(datetime.datetime.fromtimestamp(dict(res_list[2])['timestamp'] / 1000))
    # print(datetime.datetime.fromtimestamp(dict(res_list[3])['timestamp'] / 1000))
    # print(datetime.datetime.fromtimestamp(dict(res_list[4])['timestamp'] / 1000))


# 1. 잔고 확인
# 2. 이전 5분 동안의 거래량 보다 현재 20초 만에 거래량이 많고, 상승중이면
# 3. 매수를 한다
# 4. 매수 기록을 한다
# 5. 산지 100초 후에 판

if __name__ == "__main__":
    test = get_market_minute_candle("KRW-BTC", 5)
    print(test[0])
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
