import time

import requests

url = "https://api.upbit.com/v1/orderbook"

querystring = {"markets": "KRW-MTL"}
cnt = 0
status = 0

while True:
    response = requests.request("GET", url, params=querystring)
    bid_size, ask_size = 0, 0  # 매수, 매도
    total_bid_size = response.json()[0].get('total_bid_size')
    total_ask_size = response.json()[0].get('total_ask_size')
    print(total_bid_size / total_ask_size, end="\t\t")
    for i, a in enumerate(response.json()[0].get('orderbook_units')):
        ask_size += a['ask_price'] * a['ask_size']
        bid_size += a['bid_price'] * a['bid_size']
    print(bid_size / ask_size, end="\t")

    if bid_size < ask_size and status == 1:
        cnt = 0
        status = 0
    elif bid_size > ask_size and total_bid_size > total_ask_size and status == 0:
        cnt += 1
    if cnt >= 10 and status == 0:
        cnt = 0
        status = 1
    print()
    time.sleep(0.3)
