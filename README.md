1.	아이디어의 시작
이번에 만든 프로젝트는 자동 매도 프로그램 즉 트레이딩 봇이다. 나도 주식을 하고 있는 입장에서 항상 시장을 바라보고 있기에는 시간적으로 무리가 있었고 그로 인해 괜한 손해를 보는 기분이 항상 들었다. 특히 매수 타이밍을 놓쳤을 때는 그저 아쉬움만 남고 말았지만 매도 타이밍을 놓치고 떨어지는 주가를 바라볼 때에는 정말이지 고통스러운 경험으로 남았다. 리스크를 최소화하고 싶은 나는 간단한 트레이딩 봇이 있다면 얼마나 유용할까 생각하며 이 프로젝트를 시작하게 되었다.

2.	보유 종목 관리 (base.py)
가장 기본적으로 갖춰야 할 조건은 보유 종목을 관리하고 한 눈에 편하게 볼 수 있게 만드는 것이었다. 따라서 openAPI를 제공하고 있는 키움증권에 계좌를 개설한 사람들이 한 눈에 본인의 종목을 확인할 수 있도록 만들어보았다.
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

이를 통해 본인 현재 보유 종목 및 수량, 매입가 그리고 현재가를 간단히 확인할 수 있다.

3.	손절매 알리미 (warning.py)
이제 가장 먼저 할 수 있는 것은 손절매 기준을 정하고 그에 따라 알림을 보내는 기능을 코드에 추가하는 것이었다. 5% 손실을 기준으로 잡고 코드에 추가해 보았다.
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

이를 통해 손해가 발생 시 더 큰 손해를 보기 전에 알림을 받을 수 있는 구조를 만들어놨다.

4.	자동화 추가 (auto.py)
프로젝트를 진행하면서 즉각적인 반응을 할 수 있도록 만드는 것이 중요했고 이를 위해 단순 알람에서 끝나지 않고 자동적으로 매도를 해줄 수 있도록 프로그램을 고쳐보았다. 
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

이제 자동적으로 우리가 정한 기준에 도달하는 주식에 대해 매도 주문을 넣을 수 있게 되었고 우리는 매도 주문을 넣었다는 알람을 받음으로서 남들보다 빠르게 매도 타이밍을 잡을 수 있게 되었다.

5.	이득도 보기 (plus.py)
프로그램을 만들다 보니 익절 타이밍 또한 자동으로 잡을 수 있도록 만든다면 손해를 덜 볼 뿐만이 아니라 이득도 더 볼 수 있는 구조를 만들 수 있을 거라고 생각을 했고 이에 따라 프로젝트에 코드를 추가하게 되었다.
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

이로서 10% 이익 시 자동 매도, 그리고 5% 손해 시 자동 매도를 해주는 프로그램을 만들 수 있었다.

6.	흐름을 타라 (flow.py)
주식을 해본 사람들은 알겠지만 순간적인 손실과 이득에 보유 주주를 사고 파는 것은 사실 굉장히 위험한 일이다. 오히려 주식의 흐름을 보고 매수와 매도 타이밍을 잡는 것이 현명하기 때문에 내 프로젝트에도 이런 부분을 적용하기로 했다.
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

이제 연속해서 금액이 떨어지면 매도가 자동적으로 되도록 코드를 고쳤고 익절은 흐름보다는 순간적인 금액 타이밍이 중요하다고 생각했기 때문에 흐름 코드에서는 제외하였다.

7.	장타가 대세 (long.py)
지금까지는 단타에 대한 코드만을 생성했다. 하지만 나도 그렇고 요즘 주식시장은 단타만으로 살아남기 힘든 시장이라고 생각한다. 따라서 내 프로젝트를 적당히 만져 장타에 적합하도록 만들 수 있지 않을까라는 생각을 하게 되었다.
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

이제 5일간의 흐름을 분석한 뒤 명확한 하락세가 있을 때 자동 매도가 되도록 프로젝트를 고쳤고 이로 인해 전의 단타보다는 훨씬 리스크가 덜한 모양새가 될 수 있었다.

8.	기술 총집합 (whole.py)
마지막으로 더 긴 기간을 기준으로 장타를 할 수 있도록 매도 프로젝트를 바꾸면서 파이썬을 통해 주가의 흐름을 분석할 수 있다는 것을 알았기 때문에 매수하기 좋은 주식을 추천하는 기능도 살며시 넣어보았다.
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

9.	결론
주식이란 결국 흐름과 그에 따라 발생하는 타이밍 싸움이라고 볼 수 있다. 물론 이런 자동 프로그램만 믿고 주식을 하기에는 주식시장은 따져봐야 할 조건들이 너무나도 많다. 그러나 이런 프로젝트를 통해 특히나 단타로 이익을 노리는 사람은 충분히 코딩된 자동화 프로그램을 활용할 수 있지 않을까라는 생각이 들기도 하였다. 나도 알람을 받는 용으로나 모의투자를 돌려보고 할 때에는 충분히 이 프로젝트를 활용해 볼 생각을 할 것 같다.
