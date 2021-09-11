from trading_connector.AbstractTradingConnector import AbstractTradingConnector
from trading_connector.CoinTradingConnector import CoinTradingConnector
from trading_connector.StockTradingConnector import StockTradingConnector


def create(connector: str) -> AbstractTradingConnector:
    if connector == 'coin':
        return CoinTradingConnector()
    if connector == 'stock':
        return StockTradingConnector()
