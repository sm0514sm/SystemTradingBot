import time

import requests

url = "https://api.upbit.com/v1/trades/ticks"

querystring = {"market": "KRW-MTL", "count": "200"}
while True:
    response = requests.request("GET", url, params=querystring).json()

    bid_cnt, ask_cnt = 0, 0  # 매수, 매도
    bid_vol, ask_vol = 0, 0
    for a in response:
        # print(a)
        if a['ask_bid'] == 'ASK':
            ask_cnt += 1
            ask_vol += a['trade_volume']
        else:
            bid_cnt += 1
            bid_vol += a['trade_volume']

    print(f'{bid_cnt / ask_cnt:.3f} {bid_vol / ask_vol:.3f} {response[0].get("trade_price")}')
    time.sleep(1)

# orderbook이 높아지고, trade_ticks가 낮아지면 떡락
# orderbook이 낮아지고, trade_ticks가 높아지면 떡상
