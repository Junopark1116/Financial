from pykiwoom.kiwoom import Kiwoom
import time

STOP_LOSS_PERCENT = 5.0 
CHECK_INTERVAL = 60  

kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

accounts = kiwoom.GetLoginInfo("ACCNO")
account = accounts[0].strip()

def get_current_price(code):
    return float(kiwoom.GetMasterLastPrice(code).replace(',', ''))

def monitor_holdings(account):
    while True:
        try:
            holdings = kiwoom.GetStockBalance(account)

            print("\n 보유 종목 확인:")
            for stock in holdings:
                name = stock['종목명']
                code = stock['종목코드']
                quantity = int(stock['보유수량'])
                purchase_price = float(stock['매입가'])
                current_price = get_current_price(code)

                stop_loss_price = purchase_price * (1 - STOP_LOSS_PERCENT / 100)
                print(f"{name} ({code}) | 수량: {quantity} | 매입가: {purchase_price:.2f} | 현재가: {current_price:.2f}")

                if current_price <= stop_loss_price:
                    print(f"손절매 기준 도달! {name} 매도 고려 필요 (현재가: {current_price} < 손절가: {stop_loss_price:.2f})")

            time.sleep(CHECK_INTERVAL)

        except Exception as e:
            print(f"오류 발생: {e}")
            time.sleep(10)

monitor_holdings(account)
