from pykiwoom.kiwoom import Kiwoom
import time
import pandas as pd

SCREEN_NO = "1000"
TREND_DAYS = 5  
PRICE_DROP_THRESHOLD = 3.0  
CHECK_INTERVAL = 3600  

kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)
accounts = kiwoom.GetLoginInfo("ACCNO")
account = accounts[0].strip()

def get_current_price(code):
    return float(kiwoom.GetMasterLastPrice(code).replace(",", ""))

def get_recent_closes(code, days=5):
    df = kiwoom.block_request(
        "opt10081",
        종목코드=code,
        기준일자="",
        수정주가구분=1,
        output="주식일봉차트조회",
        next=0
    )
    closes = df['현재가'].astype(int).tolist()
    return closes[:days]

def evaluate_and_sell(account):
    while True:
        try:
            holdings = kiwoom.GetStockBalance(account)
            print("\n1주일 추세 기반 감시 시작")

            for stock in holdings:
                name = stock['종목명']
                code = stock['종목코드']
                quantity = int(stock['보유수량'])

                if quantity == 0:
                    continue

                closes = get_recent_closes(code, TREND_DAYS)
                if len(closes) < TREND_DAYS:
                    print(f"{name}: 데이터 부족")
                    continue

                avg_close = sum(closes[:-1]) / (TREND_DAYS - 1)
                latest_close = closes[0]  
                price_drop = (avg_close - latest_close) / avg_close * 100

                print(f"{name} ({code}) 최근 종가: {closes}")
                print(f"→ 평균: {avg_close:.2f}, 마지막: {latest_close}, 하락률: {price_drop:.2f}%")

                if price_drop >= PRICE_DROP_THRESHOLD:
                    print(f"매도 조건 만족 → 시장가 매도: {name}")
                    kiwoom.SendOrder("주간추세매도", SCREEN_NO, account, 2, code, quantity, 0, "03", "")
                    print(f"{name} 매도 주문 전송 완료!")

            time.sleep(CHECK_INTERVAL)

        except Exception as e:
            print(f"오류 발생: {e}")
            time.sleep(60)

evaluate_and_sell(account)
