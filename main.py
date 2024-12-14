import pyupbit
import time
from datetime import datetime
from pytz import timezone
import pandas as pd
from slack import SlackAPI
import json
from dotenv import load_dotenv  # pip install python-dotenv

def cal_target(ticker):
    # time.sleep(0.1)
    df_cal_target = pyupbit.get_ohlcv(ticker, "day")
    yesterday = df_cal_target.iloc[-2]
    today = df_cal_target.iloc[-1]
    yesterday_range = yesterday["high"] - yesterday["low"]
    target = today["open"] + yesterday_range * 0.5
    return target


def sell(ticker):
    # time.sleep(0.1)
    balance = upbit.get_balance(ticker)
    s = upbit.sell_market_order(ticker, balance)
    msg = str(ticker) + "매도 시도" + "\n" + json.dumps(s, ensure_ascii=False)
    print(msg)
    slack_bot.post_message(channel_id=slack_channel_id, text=msg)


def buy(ticker, money):
    # time.sleep(0.1)
    b = upbit.buy_market_order(ticker, money)
    try:
        if b["error"]:
            b = upbit.buy_market_order(ticker, 100000)
            msg = (
                "돈 좀 부족해서 "
                + str(ticker)
                + " "
                + str(100000)
                + "원 매수시도"
                + "\n"
                + json.dumps(b, ensure_ascii=False)
            )
    except:
        msg = (
            str(ticker)
            + " "
            + str(money)
            + "원 매수시도"
            + "\n"
            + json.dumps(b, ensure_ascii=False)
        )
    print(msg)
    slack_bot.post_message(channel_id=slack_channel_id, text=msg)


def printall():
    msg = f"------------------------------{now.strftime('%Y-%m-%d %H:%M:%S')}------------------------------\n"
    for i in range(n):
        msg += f"{'%10s'%coin_list[i]} 목표가: {'%11.1f'%target[i]} 현재가: {'%11.1f'%prices[i]} 매수금액: {'%7d'%money_list[i]} hold: {'%5s'%hold[i]} status: {op_mode[i]}\n"
    print(msg)


def get_yesterday_ma15(ticker):
    df_get_yesterday_ma15 = pyupbit.get_ohlcv(ticker)
    close = df_get_yesterday_ma15["close"]
    ma = close.rolling(window=5).mean()
    return ma[-2]

# 객체 생성
load_dotenv()
access = "여기에 upbit-access-key 넣어주세요"
secret = "여기에 upbit-secret-key 넣어주세요"
upbit = pyupbit.Upbit(access, secret)
token = "여기에 telegram-token-key 넣어주세요"
mc = "여기에 telegram-mc-key 넣어주세요"
bot = telegram.Bot(token)
df = pd.read_csv('dataset.csv')
df2 = pd.DataFrame(columns=['date','jonbeo','auto_upbit','difference_jonbeo_autoupbit'])

# 변수 설정
coin_list = ["KRW-BTC", "KRW-ETH", "KRW-ETC"]
n = len(coin_list)
percent_list = [0.05] * n  # 가진 돈의 5프로씩만 투자함
INF = 1000000000000
skip_list = []
n = len(coin_list)
money_list = [0] * (n)
op_mode = [False] * (n)  # 당일 9시에 코드를 시작하지 않았을 경우를 위한 변수
hold = [False] * (n)  # 해당 코인을 가지고 있는지
target = [INF] * (n)
prices = [-1] * (n)
save1 = True
save2 = True
save3 = True
time_save = True
krw_balance = 0
now = datetime.now(timezone("Asia/Seoul"))
prev_day = now.day
yesterday_ma15 = [0] * (n)
# 중간에 시작하더라도 아침 9시에 보유한 코인들을 팔 수 있게 만들었음
# print("----------현재 보유중인 코인 개수----------")
# for i in range(n):
#     time.sleep(0.1)
#     balance = upbit.get_balance(ticker=coin_list[i])
#     print("%8s"%coin_list[i]," -> ", balance, "개")
#     if balance > 0:
#         df.loc[i, 'hold'] = True
#         df.to_csv('dataset.csv', index=None)
#         hold[i] = True
# print("----------어제 ma15 가격----------")
# for i in range(n):
#     time.sleep(0.1)
#     yesterday_ma15[i] = get_yesterday_ma15(coin_list[i])
#     print(f"{'%8s'%coin_list[i]} -> {'%11.1f'%yesterday_ma15[i]} 원")
# 중간에 시작하더라도 target 데이터와 money_list 데이터 op_mode, hold데이터 가지고 옴
for i in range(n):
    target[i] = df.loc[i, "target"]
    money_list[i] = df.loc[i, "money_list"]
    hold[i] = df.loc[i, "hold"]
    op_mode[i] = df.loc[i, "op_mode"]
    yesterday_ma15[i] = df.loc[i, "yesterday_ma15"]
    if coin_list[i] in skip_list:
        op_mode[i] = False
        df.loc[i, "op_mode"] = False
        df.to_csv("dataset.csv", index=None)

while True:
    try:
        # 지금 한국 시간
        now = datetime.now(timezone("Asia/Seoul"))
        if not time_save & (now.hour - 1) % 1 == 0:
            time_save = True

        if time_save:
            save1 = True
            save2 = True
            save3 = True
            slack_bot.post_message(
                channel_id=slack_channel_id,
                blocks=[
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "🚀 업비트 코인 자동 매매 알림 💹",
                        },
                    },
                    {"type": "divider"},
                    {
                        "type": "section",
                        "fields": [{"type": "mrkdwn", "text": "자동 매매 준비 완료."}],
                    },
                    {"type": "divider"},
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "📅 *자동 매매 상태 업데이트:*\n데이터는 실시간으로 업데이트됩니다.",
                            }
                        ],
                    },
                ],
                text=":moneybag: 업비트 코인 알림",
            )
        if now.minute == 50 and save3:
            save3 = False

        # 매도 시도
        if now.minute == 59 and save1:
            time.sleep(1)
            for i in range(n):
                if hold[i] and op_mode[i]:
                    sell(coin_list[i])
                    hold[i] = False
                    df.loc[i, "hold"] = False
                    op_mode[i] = False
                    df.loc[i, "op_mode"] = False
                    df.to_csv("dataset.csv", index=None)
            print("----------전부 매도 완료----------")
            slack_bot.post_message(
                channel_id=slack_channel_id,
                blocks=[
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "🚀 업비트 코인 자동 매매 알림 💹",
                        },
                    },
                    {"type": "divider"},
                    {
                        "type": "section",
                        "fields": [{"type": "mrkdwn", "text": "*전부 매도 완료*"}],
                    },
                    {"type": "divider"},
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "📅 *자동 매매 상태 업데이트:*\n데이터는 실시간으로 업데이트됩니다.",
                            }
                        ],
                    },
                ],
                text=":moneybag: 업비트 코인 알림",
            )

            # 매도가 다 되고 나서
            time.sleep(0.1)
            krw_balance = upbit.get_balance("KRW")
            for i in range(n):
                money_list[i] = int(krw_balance * percent_list[i])
                df.loc[i, "money_list"] = money_list[i]
                df.to_csv("dataset.csv", index=None)
            msg = "----------매수할 돈 정보 갱신(money_list)----------\n"
            for i in range(n):
                msg += coin_list[i] + " " + str(money_list[i]) + "원" + "\n"
            print(msg)
            slack_bot.post_message(channel_id=slack_channel_id, text=msg)
            save1 = False
            now = datetime.now(timezone("Asia/Seoul"))

        # 목표가 갱신
        if now.minute == 00 and now.second > 30 and save2:
            for i in range(n):
                target[i] = cal_target(coin_list[i])
                op_mode[i] = True
                df.loc[i, "target"] = target[i]
                df.loc[i, "op_mode"] = True
                df.to_csv("dataset.csv", index=None)
                if coin_list[i] in skip_list:
                    op_mode[i] = False
                    df.loc[i, "op_mode"] = False
                    df.to_csv("dataset.csv", index=None)
            msg = "----------목표가 갱신(target)----------\n"
            for i in range(n):
                msg += coin_list[i] + " " + str(target[i]) + "원\n"
            print(msg)
            slack_bot.post_message(channel_id=slack_channel_id, text=msg)
            msg = "ma15 가격 갱신\n"
            for i in range(n):
                time.sleep(0.1)
                yesterday_ma15[i] = get_yesterday_ma15(coin_list[i])
                df.loc[i, "yesterday_ma15"] = yesterday_ma15[i]
                df.to_csv("dataset.csv", index=None)
                msg += (
                    "%8s" % coin_list[i]
                    + " -> "
                    + "%11.1f" % yesterday_ma15[i]
                    + "원\n"
                )
            for i in range(n):
                if yesterday_ma15[i] > target[i]:
                    msg += (
                        str(coin_list[i])
                        + "는 yesterday_ma15가 target보다 커서 안 사질 수도 있음 yesterday_ma15 -> "
                        + str(yesterday_ma15[i])
                        + " target -> "
                        + str(target[i])
                        + "\n"
                    )
            slack_bot.post_message(channel_id=slack_channel_id, text=msg)
            print(msg)
            save2 = False

        # 현 가격 가져오기
        for i in range(n):
            time.sleep(0.1)  # 실행할 때 주석처리
            prices[i] = pyupbit.get_current_price(coin_list[i])

        # 매초마다 조건을 확인한 후 매수 시도
        for i in range(n):
            if (
                op_mode[i]
                and not hold[i]
                and prices[i] >= target[i]
                and prices[i] >= yesterday_ma15[i]
            ):
                # 매수
                buy(coin_list[i], money_list[i])
                hold[i] = True
                df.loc[i, "hold"] = True
                df.to_csv("dataset.csv", index=None)
                print("----------매수 완료------------")

        # 상태 출력
        printall()
        if (now.hour % 1) == 0 and time_save:
            time_save = False
    except Exception as e:
        print(e)
        msg = e
        slack_bot.post_message(channel_id=slack_channel_id, text=msg)
