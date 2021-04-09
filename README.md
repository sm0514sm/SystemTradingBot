# CoinTradingBot

Using Upbit API
> https://docs.upbit.com/

Set your API keys on `config.ini.sample` and remove `.sample` of this file.

**You can run ONLY one strategy!!!**

## How to Start
> - `pip3 install -r requirements.txt`.
> 1.   LINUX: `source venv/bin/activate`
>   2. WINDOWS: `source venv2/bin/activate`

### 1. SM(상민) Flipping Volume Trading Strategy
> 이전 캔들의 거래량을 기반으로 현재 캔들에서 **거래량이 폭증했을 때 매수**하고 일정 시간 뒤에 매도하는 전략. (단타용)
>
> This is flipping based on the transaction volume of the previous candles.

*Run `python3 main.py`.*

**경고**: 단타를 위해 만들었으나 UPBIT API의 실시간 제공이 불안정하여 오탐률이 높습니다. Config 값을 안정적으로 설정하시길 바랍니다.

### 2. Volatility Breakout Strategy
> **현재 가격 >= 현재 캔들의 시가 + 이전 캔들의 변동성(고가 - 저가)의 일정 비율** 인 경우 매수하여, 다음 캔들에 매도하는 전략.
>
> This uses a short-term volatility breakthrough strategy.

*Run `python3 volatility_strategy.py`.*

**주의**: 단타(30분 아래 분봉)의 경우, UPBIT API 제공에 따른 실시간 가격에 오차가 있을 수 있습니다. 최소 30분봉 Config를 추천합니다.

### 3. Minimum Catch Strategy :new:

>   **현재 가격 <= 현재 캔들의 시가 + 이전 캔들의 변동성(고가 - 저가)의 일정 비율 X `N번`** 인 경우 매수하여 다음 캔들에 매도하는 전략. 즉, 저점에 매수하여 반등된 수익을 얻기위함

*Run `python3 minimum_catch_strategy.py`.*

**주의**: 거래가가 하락했을 때 매수를 추가하기 때문에, 완전한 하락세에는 매우 높은 손해를 볼 수 있습니다.

<br>