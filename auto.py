from pykiwoom.kiwoom import Kiwoom
import time

STOP_LOSS_PERCENT = 5.0    
CHECK_INTERVAL = 60         
SCREEN_NO = "1000"          

kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

accounts = kiwoom.GetLoginInfo("ACCNO")
account = accounts[0].strip()

def get_current_price(code):
    return float(kiwoom.GetMasterLastPrice(code).replace(',', ''))

def monitor_and_sell(account):
    while True:
        try:
            holdings = kiwoom.GetStockBalance(account)
            print("\n보유 종목 감시 시작:")

            for stock in holdings:
                name = stock['종목명']
                code = stock['종목코드']
                quantity = int(stock['보유수량'])
                purchase_price = float(stock['매입가'])
                current_price = get_current_price(code)

                stop_loss_price = purchase_price * (1 - STOP_LOSS_PERCENT / 100)

                print(f"{name} ({code}) | 수량: {quantity} | 매입가: {purchase_price:.2f} | 현재가: {current_price:.2f}")

                if current_price <= stop_loss_price:
                    print(f"손절매 기준 도달: {name} | 현재가: {current_price} < 손절가: {stop_loss_price:.2f}")
                    print("시장가 매도 주문 전송 중...")

                    kiwoom.SendOrder(
                        rqname="손절매도",
                        screen_no=SCREEN_NO,
                        acc_no=account,
                        order_type=2,    
                        code=code,
                        qty=quantity,
                        price=0,         
                        hoga_gb="03",    
                        org_order_no=""
                    )

                    print(f"{name} ({code}) 시장가 매도 주문 전송 완료!")

            time.sleep(CHECK_INTERVAL)

        except Exception as e:
            print(f"오류 발생: {e}")
            time.sleep(10)

monitor_and_sell(account)
