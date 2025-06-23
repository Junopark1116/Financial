from pykiwoom.kiwoom import Kiwoom
import pandas as pd
import time

SCREEN_NO = "1000"
TREND_DAYS = 60
RSI_PERIOD = 14
CHECK_INTERVAL = 3600  

kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)
account = kiwoom.GetLoginInfo("ACCNO")[0].strip()

def get_price_df(code, days=60):
    df = kiwoom.block_request(
        "opt10081",
        종목코드=code,
        기준일자="",
        수정주가구분=1,
        output="주식일봉차트조회",
        next=0
    )
    df = df[['현재가']].astype(int)
    df = df[::-1].reset_index(drop=True)  
    df.rename(columns={'현재가': 'close'}, inplace=True)
    return df.head(days)

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def analyze_stock(code, name, quantity):
    df = get_price_df(code, TREND_DAYS)
    if df.shape[0] < 60:
        print(f"{name}: 데이터 부족")
        return

    df['ma20'] = df['close'].rolling(window=20).mean()
    df['ma60'] = df['close'].rolling(window=60).mean()
    df['rsi'] = calculate_rsi(df['close'], RSI_PERIOD)

    curr_price = df['close'].iloc[-1]
    ma20 = df['ma20'].iloc[-1]
    ma60 = df['ma60'].iloc[-1]
    rsi = df['rsi'].iloc[-1]

    print(f"{name} ({code}) 현재가: {curr_price} | MA20: {ma20:.2f} | MA60: {ma60:.2f} | RSI: {rsi:.2f}")

    if quantity > 0 and (ma20 < df['ma20'].iloc[-2]) and (curr_price < ma60):
        print(f"{name}: 장기 하락 시그널 → 자동 매도")
        kiwoom.SendOrder("장기매도", SCREEN_NO, account, 2, code, quantity, 0, "03", "")
        print(f"{name} 매도 완료")

    elif quantity == 0 and curr_price > ma20 and curr_price > ma60 and rsi > 50:
        print(f"{name}: 추세 전환 감지 → 매수 추천")

def run_long_term_strategy():
    while True:
        try:
            holdings = kiwoom.GetStockBalance(account)
            print("\n장타 전략 감시 시작")

            for stock in holdings:
                name = stock['종목명']
                code = stock['종목코드']
                quantity = int(stock['보유수량'])
                analyze_stock(code, name, quantity)

            watchlist = ['005930', '035720', '000660']  
            for code in watchlist:
                name = kiwoom.GetMasterCodeName(code)
                analyze_stock(code, name, 0)

            time.sleep(CHECK_INTERVAL)

        except Exception as e:
            print(f"오류: {e}")
            time.sleep(60)

run_long_term_strategy()
