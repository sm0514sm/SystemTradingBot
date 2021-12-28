import configparser
import json
import sys
import discord_webhook

import requests
from discord_webhook import DiscordWebhook, DiscordEmbed

from object import Coin
from util import SystemValue
from util.Calculator import calculate_rate


def get_webhook_url():
    try:
        config = configparser.ConfigParser()
        config.read(f'{sys.path[0]}/config/coin_config.ini', encoding='UTF8')
        return config['DISCORD'].get("DISCORD_WEBHOOK_URL")
    except KeyError:
        return ""


def get_heartbeat_url():
    try:
        config = configparser.ConfigParser()
        config.read(f'{sys.path[0]}/config/coin_config.ini', encoding='UTF8')
        return config['DISCORD'].get("DISCORD_HEARTBEAT_URL")
    except KeyError:
        return ""


def get_daily_report_url():
    try:
        config = configparser.ConfigParser()
        config.read(f'{sys.path[0]}/config/coin_config.ini', encoding='UTF8')
        return config['DISCORD'].get("DISCORD_DAILY_REPORT_URL")
    except KeyError:
        return ""


def get_profit_rate() -> int:
    try:
        config = configparser.ConfigParser()
        config.read(f'{sys.path[0]}/config/coin_config.ini', encoding='UTF8')
        return config['CMM'].getint("PROFIT_RATE")
    except KeyError:
        return None


class DiscordConnector:
    def __init__(self, cmm_config,
                 webhook_url=get_webhook_url(),
                 heartbeat_url=get_heartbeat_url(),
                 daily_report_url=get_daily_report_url()):
        self.webhook_url = webhook_url
        self.heartbeat_url = heartbeat_url
        self.daily_report_url = daily_report_url
        self.headers = {"Content-type": "application/json"}
        self.cmm_config = cmm_config
        self.last_total_assets = 0
        self.now_total_assets = 0

    def post(self, data):
        self.headers = {"Content-type": "application/json"}
        return requests.post(self.webhook_url, headers=self.headers, data=json.dumps(data))

    def post_heartbeat(self, data):
        self.headers = {"Content-type": "application/json"}
        return requests.post(self.heartbeat_url, headers=self.headers, data=json.dumps(data))

    def post_daily_report(self, data):
        self.headers = {"Content-type": "multipart/form-data"}
        return requests.post(self.daily_report_url, headers=self.headers, data=json.dumps(data))

    def start_data(self) -> dict:
        return {
            "content": None,
            "embeds": [
                {
                    "title": "**BOT START**\n━━━━━━━━━━━━━━━━━",
                    "description": "```ini\n"
                                   f"COUNT={self.cmm_config.get('count')}            # 봉 개수\n"
                                   f"MAX_DCA_BUY_CNT={self.cmm_config.get('max_dca_buy_cnt')}  # 최대분할매수 개수\n"
                                   f"DCA_BUY_RATE={self.cmm_config.get('dca_buy_rate')}     # 분할매수 간격 비율\n"
                                   f"BUY_AMOUNT={self.cmm_config.get('buy_amount')}   # 매수당 구매양 (원)\n"
                                   f"PROFIT_RATE={self.cmm_config.get('profit_rate')}      # 매도목표 수익률```",
                    "color": 16777215
                }
            ]
        }

    def heart_data(self, now_total_assets) -> dict:
        self.now_total_assets = now_total_assets
        if self.last_total_assets == 0:
            self.last_total_assets = self.now_total_assets
        assets_dif = int(self.now_total_assets - self.last_total_assets)
        assets_dif = f'+{assets_dif:,}' if assets_dif > 0 else f'-{assets_dif:,}' if assets_dif < 0 else f'0'
        rate_of_return = calculate_rate(self.now_total_assets, self.last_total_assets)
        data = {
            "content": None,
            "embeds": [
                {
                    "title": "**HEART BEAT**\n━━━━━━━━━━━━━━━━━",
                    "description": "다행히 잘 살아있어요! 😊",
                    "color": 2010193,
                    "fields": [
                        {
                            "name": "**총 자산 변화**",
                            "value": f"{'⬆️' if rate_of_return >= 0 else '⬇️'} "
                                     f"{int(self.last_total_assets):,}원 → {int(self.now_total_assets):,}원 \n"
                                     f"({assets_dif:8}원  {rate_of_return:6.3f}%)"
                        }
                    ]
                }
            ]
        }
        self.last_total_assets = self.now_total_assets
        return data

    @staticmethod
    def buy_data(coin: Coin) -> dict:
        avg_buy = int(coin.avg_buy_price) if coin.avg_buy_price > 10 else round(coin.avg_buy_price, 2)
        target_buy = round(coin.target_buy_price) if coin.target_buy_price > 10 else round(coin.target_buy_price, 2)
        sell_price = min(coin.cmm_info.max, get_profit_rate())
        target_sell = round(sell_price) if sell_price > 10 else round(sell_price, 2)
        current = round(coin.current_price) if coin.current_price > 10 else round(coin.current_price, 2)
        buy_cnt = round(coin.buy_volume_cnt) if coin.buy_volume_cnt > 100 \
            else round(coin.buy_volume_cnt, 3) if coin.buy_volume_cnt > 10 \
            else round(coin.buy_volume_cnt, 4) if coin.buy_volume_cnt > 1 \
            else round(coin.buy_volume_cnt, 6)
        return {
            "content": None,
            "embeds": [
                {
                    "title": f"**{coin.name} 매수**\n━━━━━━━━━━━━━━━━━",
                    "color": 16711680,
                    "fields": [
                        {
                            "name": "🔸 **매수한 개수**",
                            "value": f"{buy_cnt:,} 개"
                        },
                        {
                            "name": "🔸 **매수 평균가**",
                            "value": f"{avg_buy:,} 원 "
                        },
                        {
                            "name": "🔸 **현재 매수가**",
                            "value": f"{current:,} 원"
                        },
                        {
                            "name": "🔸 **매수 횟수**",
                            "value": f"{coin.dca_buy_cnt} 번"
                        },
                        {
                            "name": "🔸 **Next Target Buy Price**",
                            "value": f"{target_buy:,} 원 "
                        },
                        {
                            "name": "🔸 **Target Sell Price (변할 수 있음)**",
                            "value": f"{target_sell:,} 번"
                        }
                    ]
                }
            ]
        }

    @staticmethod
    def sell_data(coin: Coin):
        avg_buy = int(coin.avg_buy_price) if coin.avg_buy_price > 1 else round(coin.avg_buy_price, 1)
        avg_sell = int(coin.avg_sell_price) if coin.avg_sell_price > 1 else round(coin.avg_sell_price, 1)
        rate_of_return = calculate_rate(coin.avg_sell_price, coin.avg_buy_price)
        return {
            "content": None,
            "embeds": [
                {
                    "title": f"**{coin.name} 매도 **\n━━━━━━━━━━━━━━━━━",
                    "color": 1597146,
                    "fields": [
                        {
                            "name": "🔹 **매도한 개수**",
                            "value": f"{coin.buy_volume_cnt} 개"
                        },
                        {
                            "name": "🔹 **매수 평균가 -> 매도 평균가**",
                            "value": f"{avg_buy:,} 원 -> {avg_sell:,} 원"
                        },
                        {
                            "name": "🔹 **평가손익 (수익률)**",
                            "value": f"{'⬆️' if rate_of_return >= 0 else '⬇️'} "
                                     f"{coin.sold_amount - coin.bought_amount:,.0f} 원 "
                                     f"({rate_of_return:.2f} %)"
                        }
                    ]
                }
            ]
        }

    def daily_report_data(self, filename: str):
        webhook = DiscordWebhook(url=self.daily_report_url)

        with open(filename, "rb") as f:
            webhook.add_file(file=f.read(), filename=filename)
        webhook.execute()


########################################################################################################################


def test_buy_data():
    connector = DiscordConnector(None)
    coin = Coin.Coin("BTC")
    coin.buy_volume_cnt = 52.256234
    coin.avg_buy_price = 126437.246
    coin.dca_buy_cnt = 3
    connector.post(DiscordConnector.buy_data(coin))


def test_sell_data():
    connector = DiscordConnector(None)
    coin = Coin.Coin("BTC")
    coin.buy_volume_cnt = 52.256234
    coin.avg_buy_price = 126437.246
    coin.avg_sell_price = 137564.65
    coin.bought_amount = coin.avg_buy_price * coin.buy_volume_cnt
    coin.sold_amount = coin.avg_sell_price * coin.buy_volume_cnt
    coin.dca_buy_cnt = 3
    connector.post(DiscordConnector.sell_data(coin))


def test_start_data():
    connector = DiscordConnector({'count': 30, 'max_dca_buy_cnt': 10, 'profit_rate': 50,
                                  'dca_buy_rate': 10, 'buy_amount': 100000})
    connector.post(connector.start_data())


def test_heart_data():
    connector = DiscordConnector(None)
    connector.post_heartbeat(connector.heart_data(3350863))
    connector.post_heartbeat(connector.heart_data(4350863))
    connector.post_heartbeat(connector.heart_data(5350863))


def test_daily_report_data():
    connector = DiscordConnector(None)
    connector.daily_report_data(f"{SystemValue.root_path()}/daily_report/20211109-20211209.png")
    # connector.post_daily_report(connector.daily_report_data())
