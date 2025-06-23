from pykiwoom.kiwoom import Kiwoom
import time

TREND_MINUTES = 3            
CHECK_INTERVAL = 60         
SCREEN_NO = "1000"           
TARGET_CODES = []            

kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)
accounts = kiwoom.GetLoginInfo("ACCNO")
account = accounts[0].strip()

price_history = {}

def get_current_price(code):
    return float(kiwoom.GetMasterLastPrice(code).replace(',', ''))

def monitor_trend_and_sell(account):
    while True:
        try:
            holdings = kiwoom.GetStockBalance(account)
            print("\n가격 흐름 감시:")

            for stock in holdings:
                name = stock['종목명']
                code = stock['종목코드']
                quantity = int(stock['보유수량'])

                if quantity == 0:
                    continue
                if TARGET_CODES and code not in TARGET_CODES:
                    continue

                current_price = get_current_price(code)

                if code not in price_history:
                    price_history[code] = []
                price_history[code].append(current_price)
                if len(price_history[code]) > TREND_MINUTES:
                    price_history[code].pop(0)

                print(f"{name} ({code}) 현재가: {current_price:.2f} | 최근 {len(price_history[code])}분 가격: {price_history[code]}")

                prices = price_history[code]
                if len(prices) == TREND_MINUTES and all(prices[i] > prices[i+1] for i in range(len(prices)-1)):
                    print(f"연속 하락 감지: {name} → 시장가 매도 실행")
                    kiwoom.SendOrder("트렌드매도", SCREEN_NO, account, 2, code, quantity, 0, "03", "")
                    print(f"{name} ({code}) 매도 완료")
                    price_history[code] = []  

            time.sleep(CHECK_INTERVAL)

        except Exception as e:
            print(f"오류 발생: {e}")
            time.sleep(10)

monitor_trend_and_sell(account)
