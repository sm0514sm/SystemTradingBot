import jwt
import uuid
import hashlib
import time
from urllib.parse import urlencode
import requests


def buy_stock(access_key: str, secret_key: str, market: str, price: float) -> list:
    """Order a specified stock buyout. (market price)
    :param access_key: See the file "config.ini"
    :param secret_key: See the file "config.ini"
    :param market: Market id to trade
    :param price: Price to trade
    :return: list
    """
    query = {
        'market': market,
        'side': 'bid',
        'price': price,
        'ord_type': 'price',
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post("https://api.upbit.com/v1/orders", params=query, headers=headers)
    time.sleep(3)
    return res.json()


'''
주문 가능 금액 초과: {'error': {'message': '주문가능한 금액(KRW)이 부족합니다.', 'name': 'insufficient_funds_bid'}} 
market 이름 오류: {'error': {'message': 'market does not have a valid value', 'name': 'validation_error'}} 
Success
{'uuid': '29fb1604-de7c-4462-8fc8-c98b20d15780', 'side': 'bid', 'ord_type': 'price', 'price': '5001.12', 
'state': 'wait', 'market': 'KRW-ETH', 'created_at': '2021-02-23T17:41:31+09:00', 'volume': None, 
'remaining_volume': None, 'reserved_fee': '2.50056', 'remaining_fee': '2.50056', 'paid_fee': '0.0', 
'locked': '5003.62056', 'executed_volume': '0.0', 'trades_count': 0} 
'''


def sell_stock(access_key: str, secret_key: str, market: str, volume: float) -> list:
    """Order a specified stock sellout. (market price)
    :param access_key: See the file "config.ini"
    :param secret_key: See the file "config.ini"
    :param market: Market id to trade
    :param volume: Volume to trade
    :return: list
    """
    query = {
        'market': market,
        'side': 'ask',
        'volume': volume,
        'ord_type': 'market',
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post("https://api.upbit.com/v1/orders", params=query, headers=headers)
    time.sleep(3)
    return res.json()


'''
:except
최대 거래 금액 초과: {'error': {'message': '최대 주문 금액은 1000000000.0 KRW입니다. 시장가 매도시 주문금액은 주문 수량 * 매수 1호가로 계산합니다.', 'name': 'over_max_total_market_ask'}}
보유 코인 금액 초과: {'error': {'message': '주문가능한 금액(ETH)이 부족합니다.', 'name': 'insufficient_funds_ask'}}
'''
