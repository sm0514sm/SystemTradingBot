import jwt
import uuid
import hashlib
import time
from urllib.parse import urlencode
import requests


def buy_stock(access_key: str, secret_key: str, market: str, price: float, sleep: float = 3.0) -> dict:
    query = {
        'market': market,
        'side': 'bid',
        'price': price,
        'ord_type': 'price',
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


def sell_stock(access_key: str, secret_key: str, market: str, volume: float, sleep: float = 3.0) -> dict:
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
