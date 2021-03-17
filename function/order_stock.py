import jwt
import uuid
import hashlib
import time
from urllib.parse import urlencode
import requests
import configparser

config = configparser.ConfigParser()
config.read('config.ini', encoding='UTF8')
try:
    access_key: str = config['UPBIT']['UPBIT_OPEN_API_ACCESS_KEY']
    secret_key: str = config['UPBIT']['UPBIT_OPEN_API_SECRET_KEY']
except KeyError:
    config.read('../config.ini', encoding='UTF8')
    access_key: str = config['UPBIT']['UPBIT_OPEN_API_ACCESS_KEY']
    secret_key: str = config['UPBIT']['UPBIT_OPEN_API_SECRET_KEY']


def buy_stock(market: str, price: float, sleep: float = 2.0, volume: float = 0, ord_type: str = "price") -> dict:
    if (ord_type == "price" and volume != 0) or (ord_type == "limit" and volume == 0):
        print("뭔가 이상함")
        return dict()
    if volume:
        query = {
            'market': market,
            'side': 'bid',
            'volume': volume,
            'price': price,
            'ord_type': ord_type,
        }
    else:
        query = {
            'market': market,
            'side': 'bid',
            'price': price,
            'ord_type': ord_type,
        }
    m = hashlib.sha512()
    m.update(urlencode(query).encode())
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
    time.sleep(sleep)
    return res.json()


def sell_stock(market: str, volume: float, sleep: float = 2.0) -> dict:
    query = {
        'market': market,
        'side': 'ask',
        'volume': volume,
        'ord_type': 'market',
    }
    m = hashlib.sha512()
    m.update(urlencode(query).encode())
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
    time.sleep(sleep)
    return res.json()


def get_total_buy_price(market) -> float:
    query = {
        'market': f'KRW-{market}',
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

    res = requests.get("https://api.upbit.com/v1/orders/chance", params=query, headers=headers).json()
    ask_account = res.get('ask_account')
    return float(ask_account.get('balance')) * float(ask_account.get('avg_buy_price'))


def get_total_sell_price(uuid_value):
    query = {
        'uuid': uuid_value,
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

    res = requests.get("https://api.upbit.com/v1/order", params=query, headers=headers).json()
    print("get_total_sell_price: res", res, res.get('paid_fee'))
    sell_price = -float(res.get('paid_fee'))
    for trade in res.get('trades'):
        sell_price += float(trade.get('price')) * float(trade.get('volume'))
    return sell_price


def cancel_buy(uuid_value):
    query = {
        'uuid': uuid_value,
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

    res = requests.delete("https://api.upbit.com/v1/order", params=query, headers=headers)

    print(res.json())
