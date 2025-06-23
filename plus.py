from pykiwoom.kiwoom import Kiwoom
import time

STOP_LOSS_PERCENT = 5.0    
TAKE_PROFIT_PERCENT = 10.0 
CHECK_INTERVAL = 60        
SCREEN_NO = "1000"          

kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

accounts = kiwoom.GetLoginInfo("ACCNO")
account = accounts[0].strip()

def get_current_price(code):
    return float(kiwoom.GetMasterLastPrice(code).replace(',', ''))

def monitor_and_trade(account):
    while True:
        try:
            holdings = kiwoom.GetStockBalance(account)
            print("\n보유 종목 감시:")

            for stock in holdings:
                name = stock['종목명']
                code = stock['종목코드']
                quantity = int(stock['보유수량'])
                purchase_price = float(stock['매입가'])

                if quantity == 0:
                    continue

                current_price = get_current_price(code)
                stop_loss_price = purchase_price * (1 - STOP_LOSS_PERCENT / 100)
                take_profit_price = purchase_price * (1 + TAKE_PROFIT_PERCENT / 100)

                print(f"{name} ({code}) | 수량: {quantity} | 매입가: {purchase_price:.2f} | 현재가: {current_price:.2f}")

                if current_price <= stop_loss_price:
                    print(f"손절매 기준 도달: {name} | 현재가: {current_price} < 손절가: {stop_loss_price:.2f}")
                    print("시장가 매도(손절) 주문 전송 중...")
                    kiwoom.SendOrder("손절매도", SCREEN_NO, account, 2, code, quantity, 0, "03", "")
                    print(f"{name} 손절 매도 주문 완료!")

                elif current_price >= take_profit_price:
                    print(f"익절 기준 도달: {name} | 현재가: {current_price} > 익절가: {take_profit_price:.2f}")
                    print("시장가 매도(익절) 주문 전송 중...")
                    kiwoom.SendOrder("익절매도", SCREEN_NO, account, 2, code, quantity, 0, "03", "")
                    print(f"{name} 익절 매도 주문 완료!")

            time.sleep(CHECK_INTERVAL)

        except Exception as e:
            print(f"오류 발생: {e}")
            time.sleep(10)

monitor_and_trade(account)
