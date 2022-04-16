from strategy_type.AbstractStrategy import AbstractStrategy
from strategy_type.CatchMinMax import CatchMinMax
from strategy_type.ShortVolatilityBreakout import ShortVolatilityBreakout


def create(strategy: str, trading_connector) -> AbstractStrategy:
    match strategy:
        case 'CMM':
            return CatchMinMax(trading_connector)
        case'SVB':
            return ShortVolatilityBreakout(trading_connector)
