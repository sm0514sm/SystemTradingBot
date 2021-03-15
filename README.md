# CoinTradingBot

Using Upbit API
> https://docs.upbit.com/

Set your API keys on `config.ini.sample` and remove `.sample` of this file.

## How to Start
> - `pip3 install -r requirements.txt`.
> 
>   1.   LINUX: `source venv/bin/activate`
>   2. WINDOWS: `source venv2/bin/activate`

### 1. SM(상민) Trading Strategy
> This is flipping based on the transaction volume of the previous candles.

*Run `python3 main.py`.*

### 2. Volatility Breakout Strategy
> This uses a short-term volatility breakthrough strategy.

*Run `python3 volatility_strategy.py`.*