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
            print(get_now_coin_info(f"KRW-BTC", sleep=0.5).get('trade_price'))
        except json.decoder.JSONDecodeError:
            pass
