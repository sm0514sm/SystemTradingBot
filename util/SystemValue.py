import sys


def root_path():
    idx = sys.path[0].find("SystemTradingBot")
    return sys.path[0][:idx + len("SystemTradingBot")]