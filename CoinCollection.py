from Coin import Coin


class CoinCollection:
    def __init__(self, collector_name, coin_name_list):
        self.name = collector_name
        self.coins: list = [Coin(coin_name) for coin_name in coin_name_list]

    def buy_all(self):
        for coin in self.coins:
            coin.buy_coin()