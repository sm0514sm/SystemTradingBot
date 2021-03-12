import uuid
import jwt
import requests


def get_account(access_key: str, secret_key: str) -> list:
    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
    }

    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get('https://api.upbit.com/v1/accounts', headers=headers)

    return res.json()
