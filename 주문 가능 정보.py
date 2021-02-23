import os
import jwt
import json
import uuid
import hashlib
from urllib.parse import urlencode
import configparser
import requests

config = configparser.ConfigParser()
config.read('config.ini')
access_key = config['UPBIT']['UPBIT_OPEN_API_ACCESS_KEY']
secret_key = config['UPBIT']['UPBIT_OPEN_API_SECRET_KEY']
query = {
    'market': 'KRW-ETH',
    'nonce': str(uuid.uuid4()),
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

res = requests.get('https://api.upbit.com/v1/orders/chance', params=query, headers=headers)
print(json.dumps(dict(res.json()), indent=2))
