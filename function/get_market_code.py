import requests


def get_market_code() -> list:
    """Returns the list of market codes
    :return: list
    """
    querystring = {"isDetails": "false"}
    response = requests.request("GET", "https://api.upbit.com/v1/market/all", params=querystring)
    market_codes = []
    for data in response.json():
        if 'KRW-' not in data['market']:
            continue
        market_codes.append(data['market'])
    return market_codes


if __name__ == '__main__':
    print(get_market_code())
