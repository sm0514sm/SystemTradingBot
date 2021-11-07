import requests
import json

webhook_url = "https://discord.com/api/webhooks/906919542226305034/mEfkIJBBRMsBq_iC2f3Q9Fua0JZ65aH2fMcRN5YYRZqpmWW7QbEvh95bCL1g8JWajcbU"

headers = {
    "Content-type": "application/json"
}

buy_data = {
    "content": None,
    "embeds": [
        {
            "title": "**BTC 매수**\n━━━━━━━━━━━━━━━━━",
            "color": 16711680,
            "fields": [
                {
                    "name": "🔸 **매수한 개수**",
                    "value": "41.325 개"
                },
                {
                    "name": "🔸 **매수 평균가**",
                    "value": "315.152 원"
                },
                {
                    "name": "🔸 **매수 횟수**",
                    "value": "2 번"
                }
            ]
        }
    ]
}
sell_data = {
    "content": None,
    "embeds": [
        {
            "title": "**BTC 매도 **\n━━━━━━━━━━━━━━━━━",
            "color": 1597146,
            "fields": [
                {
                    "name": "🔹 **매도한 개수**",
                    "value": "41.325 개"
                },
                {
                    "name": "🔹 **매수 평균가 -> 매도 평균가**",
                    "value": "301.562 원 -> 315.152 원"
                },
                {
                    "name": "🔹 **평가손익 (수익률)**",
                    "value": "⬆️ 59845 원 (4.05%)"
                }
            ]
        }
    ]
}
heart_data = {
    "content": None,
    "embeds": [
        {
            "title": "**HEART BEAT**\n━━━━━━━━━━━━━━━━━",
            "description": "다행히 잘 살아있어요! 😊",
            "color": 2010193,
            "fields": [
                {
                    "name": "**총 자산 변화**",
                    "value": "⬆️ 3,151,150 원 → 3,161,175 원 (0.25 %)"
                }
            ]
        }
    ]
}
start_data = {
    "content": None,
    "embeds": [
        {
            "title": "**BOT START**\n━━━━━━━━━━━━━━━━━",
            "description": "```ini\n"
                           "COUNT=15            # 봉 개수\n"
                           "MAX_DCA_BUY_CNT=10  # 최대분할매수 개수\n"
                           "DCA_BUY_RATE=10     # 분할매수 간격 비율\n"
                           "BUY_AMOUNT=100000   # 매수당 구매양 (원)\n"
                           "PROFIT_RATE=50      # 매도목표 수익률```",
            "color": 16777215
        }
    ]
}
res = requests.post(webhook_url, headers=headers, data=json.dumps(start_data))
res = requests.post(webhook_url, headers=headers, data=json.dumps(sell_data))
res = requests.post(webhook_url, headers=headers, data=json.dumps(buy_data))
res = requests.post(webhook_url, headers=headers, data=json.dumps(heart_data))
print(res.status_code)
