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

<br>

## Plan

### New Strategy

#### SM Fall Rebound Split Buying Strategy

> 코인의 매수를 현재 캔들에서 아래의 일정 비율로 매수 예약 -> 캔들이 바뀌면 매도 or 일정 수익률 이상이면 매도

### New Features

#### Volatility Breakout Strategy

- Asynchronous ordering with Asyncio.
- Determining the purchase price based on the conditions