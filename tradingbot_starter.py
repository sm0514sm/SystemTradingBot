import sys
import logging

from strategy_type import StrategyFactory
from strategy_type.AbstractStrategy import AbstractStrategy
from trading_connector import TradingConnectorFactory
from trading_connector.AbstractTradingConnector import AbstractTradingConnector
from util.ColorFormatter import ColorFormatter

trading_connector_list = ["coin", "stock"]
strategy_list = ["FV", "VB", "CM", "CMM"]


def logger_setting():
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(ColorFormatter())
    logger.addHandler(ch)


def is_valid_strategy(strategy):
    if strategy in strategy_list:
        logger.info(f'strategy: "{strategy}"')
        return True
    else:
        logger.error(f'잘못된 strategy("{strategy}"). {strategy_list}에서 선택.')
        return False


def is_valid_trading(trading):
    if trading in trading_connector_list:
        logger.info(f'trading_type: "{trading}"')
        return True
    else:
        logger.error(f'잘못된 trading_connector("{trading}"). {trading_connector_list}에서 선택.')
        return False


if __name__ == "__main__":
    logger = logging.getLogger("SystemLogger")
    logger_setting()
    if len(sys.argv) != 3:
        logger.error("입력 인자 개수가 부족합니다. (사용예시: 'python tradingbot_starter.py coin CMM')")
        exit()
    trading_connector_type = sys.argv[1]
    strategy_type = sys.argv[2]
    if not is_valid_trading(trading_connector_type) or not is_valid_strategy(strategy_type):
        exit()
    trading_connector: AbstractTradingConnector = TradingConnectorFactory.create(trading_connector_type)
    strategy: AbstractStrategy = StrategyFactory.create(strategy_type, trading_connector)
    strategy.run_strategy()
