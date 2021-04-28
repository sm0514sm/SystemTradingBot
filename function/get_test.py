import time

import requests

url1 = "https://api.upbit.com/v1/orderbook"
url2 = "https://api.upbit.com/v1/trades/ticks"

market_name = "KRW-hunt"


while True:
    querystring = {"markets": market_name}
    response1 = requests.request("GET", url1, params=querystring).json()
    bid_size, ask_size = 0, 0  # 매수, 매도
    total_bid_size = response1[0].get('total_bid_size')
    total_ask_size = response1[0].get('total_ask_size')
    print(total_bid_size / total_ask_size, end="\t\t")
    for i, a in enumerate(response1[0].get('orderbook_units')):
        ask_size += a['ask_price'] * a['ask_size']
        bid_size += a['bid_price'] * a['bid_size']
    print(bid_size / ask_size, end="\t")

    querystring = {"market": market_name, "count": "200"}
    response2 = requests.request("GET", url2, params=querystring).json()

    bid_cnt, ask_cnt = 0, 0  # 매수, 매도
    bid_vol, ask_vol = 0, 0
    for a in response2:
        # print(a)
        if a['ask_bid'] == 'ASK':
            ask_cnt += 1
            ask_vol += a['trade_volume']
        else:
            bid_cnt += 1
            bid_vol += a['trade_volume']

    print(f'{bid_cnt / ask_cnt:.3f} {bid_vol / ask_vol:.3f} {response2[0].get("trade_price")}')
    time.sleep(0.5)

# orderbook이 높아지고, trade_ticks가 낮아지면 떡락
# orderbook이 낮아지고, trade_ticks가 높아지면 떡상
