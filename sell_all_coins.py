from object.Coin import Coin
from trading_connector.CoinTradingConnector import CoinTradingConnector

if __name__ == "__main__":
    connector = CoinTradingConnector()
    for _ in range(3): # 왠지 모르게 3번은 반복해야 모두 삭제됨
        for coin in connector.get_balances():
            print(coin.get('currency'))
            print(coin.get('balance'))
            connector.upbit.sell_market_order(f"KRW-{coin.get('currency')}", coin.get('balance'))