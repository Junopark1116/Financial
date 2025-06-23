pip install pykiwoom

from pykiwoom.kiwoom import Kiwoom
import time

kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

accounts = kiwoom.GetLoginInfo("ACCNO")
account = accounts[0].strip()

def get_holdings(account):
    holdings = kiwoom.GetStockBalance(account)
    print("보유 종목:")
    for stock in holdings:
        name = stock['종목명']
        code = stock['종목코드']
        quantity = stock['보유수량']
        purchase_price = stock['매입가']
        current_price = kiwoom.GetMasterLastPrice(code)

        print(f"{name} ({code}) | 수량: {quantity} | 매입가: {purchase_price} | 현재가: {current_price}")
    return holdings

get_holdings(account)
