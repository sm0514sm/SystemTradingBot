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

**경고**: 불안정하여 오탐률이 높습니다. Config 값을 안정적으로 설정하시길 바랍니다.

### 2. Volatility Breakout Strategy
> This uses a short-term volatility breakthrough strategy.

*Run `python3 volatility_strategy.py`.*

**주의**: 단타(30분 아래 분봉)의 경우, UPBIT API 제공에 따른 실시간 가격에 오차가 있을 수 있습니다. 최소 30분봉 Config를 추천합니다.