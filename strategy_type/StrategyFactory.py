from strategy_type.AbstractStrategy import AbstractStrategy
from strategy_type.CatchMinMax import CatchMinMax


def create(strategy: str, trading_connector) -> AbstractStrategy:
    if strategy == 'CMM':
        return CatchMinMax(trading_connector)
    if strategy == 'CM':
        pass
