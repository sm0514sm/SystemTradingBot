import uuid
import jwt
import requests
import configparser
from function.order_stock import sell_stock
from trading_connector.CoinTradingConnector import CoinTradingConnector


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
    connector = CoinTradingConnector()
    access_key = connector.access
    secret_key = connector.secret
    # 계정 내 모든 코인 팔기
    for account in get_account():
        if account['currency'] in ['KRW']:
            continue
        sell_stock("KRW-" + account['currency'], account['balance'], sleep=0.2)
        print(account)
