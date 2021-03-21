import uuid
import jwt
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


def get_account() -> list:
    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
    }

    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get('https://api.upbit.com/v1/accounts', headers=headers)

    return res.json()


if __name__ == "__main__":
    # 계정 내 모든 코인 정보
    for account in get_account():
        if account['currency'] == 'KRW':
            continue
        print(round(float(account['balance']) * float(account['avg_buy_price'])), account)
