from object.Coin import Coin
from trading_connector.CoinTradingConnector import CoinTradingConnector

if __name__ == "__main__":
    y = input("WARNING: 소유하고 있는 모든 코인을 시장가에 매도 합니다. 확인 = 'y'\n ==> ")
    if y != 'y':
        exit()
    connector = CoinTradingConnector()
    for _ in range(3):  # 왠지 모르게 3번은 반복해야 모두 삭제됨
        for coin in connector.get_balances():
            print(f"{coin.get('currency')} 코인 {coin.get('balance')}개 매도")
            connector.upbit.sell_market_order(f"KRW-{coin.get('currency')}", coin.get('balance'))
