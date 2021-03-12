import requests


def get_market_code(div_cnt=1, maximum=0, except_krw=True) -> list:
    """KRW 코인 마켓 리스트를 출력함
    Args:
        div_cnt (int): 나눌 개수
        maximum (int): 최대 제한 (0 무제한)
        except_krw (bool): "KRW-" 제거 여부
    Returns:
        list:
    """
    querystring = {"isDetails": "false"}
    response = requests.request("GET", "https://api.upbit.com/v1/market/all", params=querystring)

    KRW_markets = []
    market_codes = []
    codes = []

    for data in response.json():
        if 'KRW-' not in data['market']:
            continue
        KRW_markets.append(data['market'][4:])

    len_codes = maximum if maximum != 0 else len(KRW_markets) // div_cnt
    for market in KRW_markets:
        codes.append(market)
        if len(codes) == len_codes:
            market_codes.append(codes[:])
            codes.clear()
        if len(market_codes) == div_cnt:
            break
    return market_codes


if __name__ == '__main__':
    codess = get_market_code(div_cnt=3, maximum=20)
    print(f'list 개수: {len(codess)}\n')
    for i, cod in enumerate(codess):
        print(f'{i}번째({len(cod)}개): {cod}')
