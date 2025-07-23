import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI

import pyupbit

load_dotenv()

def get_market_data():
    """시장 데이터 수집"""
    import pyupbit
    
    try:
        # 1. 30일 일봉 데이터
        daily_df = pyupbit.get_ohlcv("KRW-BTC", count=30, interval='day')
        
        # 2. 24시간 시간봉 데이터
        hourly_df = pyupbit.get_ohlcv("KRW-BTC", count=24, interval='minute60')
        
        # 3. 현재 가격
        current_price = pyupbit.get_current_price("KRW-BTC")
        
        # 4. 오더북 (호가 정보)
        orderbook = pyupbit.get_orderbook(ticker="KRW-BTC")
        
        return {
            "daily_ohlcv": daily_df.to_json(),
            "hourly_ohlcv": hourly_df.to_json(),
            "current_price": current_price,
            "orderbook": orderbook
        }
    except Exception as e:
        print(f"시장 데이터 수집 오류: {e}")
        return None

def get_investment_status(upbit):
    """현재 투자 상태 조회"""
    
    try:
        # 전체 잔고 조회
        balances = upbit.get_balances()
        
        # KRW 잔고
        krw_balance = upbit.get_balance("KRW")
        
        # BTC 잔고
        btc_balance = upbit.get_balance("KRW-BTC") or 0
        
        # 현재 BTC 가격
        current_price = pyupbit.get_current_price("KRW-BTC")
        
        # BTC 평가금액
        btc_value = btc_balance * current_price if btc_balance else 0
        
        # 총 자산 (KRW + BTC 평가금액)
        total_asset = krw_balance + btc_value
        
        # 미체결 주문 조회
        pending_orders = upbit.get_order("KRW-BTC", state="wait")
        
        investment_status = {
            "krw_balance": krw_balance,
            "btc_balance": btc_balance,
            "btc_avg_buy_price": None,
            "btc_current_price": current_price,
            "btc_value": btc_value,
            "total_asset": total_asset,
            "pending_orders_count": len(pending_orders) if pending_orders else 0
        }
        
        # BTC 평균 매수가 찾기
        for balance_info in balances:
            if balance_info['currency'] == 'BTC':
                investment_status["btc_avg_buy_price"] = float(balance_info.get('avg_buy_price', 0))
                break
        
        return investment_status
        
    except Exception as e:
        print(f"투자 상태 조회 오류: {e}")
        return None

def get_ai_recommendation(market_data, investment_status):
    """AI를 통한 매매 추천"""
    try:
        client = OpenAI()
        
        # AI에게 제공할 데이터 구성
        analysis_data = {
            "market_data": market_data,
            "investment_status": investment_status
        }
        
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": '''당신은 전문 비트코인 트레이더입니다. 제공된 데이터를 분석하여 매매 결정을 내리세요.

                    분석할 데이터:
                    1. daily_ohlcv: 30일 일봉 데이터 (OHLCV)
                    2. hourly_ohlcv: 24시간 시간봉 데이터 (OHLCV) 
                    3. current_price: 현재 비트코인 가격
                    4. orderbook: 매수/매도 호가 정보
                    5. investment_status: 현재 투자 상태 (보유 현금, BTC 수량, 평균 매수가 등)

                    분석 요소:
                    - 가격 트렌드 (단기/장기)
                    - 이동평균선 패턴
                    - RSI, MACD 등 기술적 지표
                    - 거래량 분석
                    - 지지/저항선 분석
                    - 호가창 분석 (매수/매도 압력)
                    - 현재 포지션 대비 리스크 관리

                    응답은 반드시 JSON 형식으로 제공해주세요:
                    {
                        "recommendation": "buy" | "sell" | "hold",
                        "confidence": 1-10 (확신도),
                        "justification": "1-2문장 설명",
                        "risk_level": "low" | "medium" | "high"
                    }'''
                },
                {
                    "role": "user", 
                    "content": f"다음 데이터를 분석하여 JSON 형식으로 매매 추천을 해주세요: {json.dumps(analysis_data, ensure_ascii=False)}"
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=1024
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except json.JSONDecodeError as e:
        print(f"JSON 파싱 오류: {e}")
        # 기본 추천 반환
        return get_fallback_recommendation(investment_status)
    except Exception as e:
        print(f"AI 분석 오류: {e}")
        # 기본 추천 반환
        return get_fallback_recommendation(investment_status)

def get_fallback_recommendation(investment_status):
    """AI 분석 실패 시 기본 추천"""
    import pyupbit
    
    try:
        # 간단한 기술적 분석 기반 추천
        df = pyupbit.get_ohlcv("KRW-BTC", count=5, interval='day')
        current_price = pyupbit.get_current_price("KRW-BTC")
        
        # 5일 평균가 계산
        avg_price = df['close'].mean()
        
        # 현재가가 평균가보다 낮으면 매수, 높으면 보유
        if current_price < avg_price * 0.98:  # 2% 이하일 때 매수
            return {
                "recommendation": "buy",
                "confidence": 5,
                "justification": "현재가가 5일 평균가 대비 2% 이상 하락하여 매수 기회로 판단",
                "risk_level": "medium"
            }
        elif current_price > avg_price * 1.05:  # 5% 이상 상승 시 매도
            return {
                "recommendation": "sell", 
                "confidence": 5,
                "justification": "현재가가 5일 평균가 대비 5% 이상 상승하여 수익 실현",
                "risk_level": "medium"
            }
        else:
            return {
                "recommendation": "hold",
                "confidence": 6,
                "justification": "현재 가격이 적정 범위 내에 있어 보유 권장",
                "risk_level": "low"
            }
            
    except Exception as e:
        print(f"기본 분석도 실패: {e}")
        return {
            "recommendation": "hold",
            "confidence": 3,
            "justification": "분석 실패로 인한 안전한 보유 권장",
            "risk_level": "high"
        }

def execute_trade(upbit, recommendation, investment_status):
    """매매 실행"""
    try:
        action = recommendation.get("recommendation")
        confidence = recommendation.get("confidence", 0)
        risk_level = recommendation.get("risk_level", "high")
        
        # 신뢰도가 낮으면 거래하지 않음
        if confidence < 6:
            print(f"신뢰도가 낮아 거래를 건너뜁니다. 신뢰도: {confidence}")
            return
        
        # 리스크가 너무 높으면 거래량 조절
        trade_ratio = 0.1 if risk_level == "high" else 0.2 if risk_level == "medium" else 0.3
        
        if action == "buy":
            krw_balance = investment_status["krw_balance"]
            if krw_balance > 5000:  # 최소 거래 금액 확인
                buy_amount = krw_balance * trade_ratio
                print(f"매수 실행: {buy_amount:,.0f}원")
                result = upbit.buy_market_order("KRW-BTC", buy_amount)
                print(f"매수 결과: {result}")
            else:
                print("매수 가능한 KRW 잔액이 부족합니다.")
                
        elif action == "sell":
            btc_balance = investment_status["btc_balance"]
            btc_value = investment_status["btc_value"]
            
            if btc_balance > 0 and btc_value > 5000:  # 최소 거래 금액 확인
                sell_amount = btc_balance * trade_ratio
                print(f"매도 실행: {sell_amount:.8f} BTC")
                result = upbit.sell_market_order("KRW-BTC", sell_amount)
                print(f"매도 결과: {result}")
            else:
                print("매도 가능한 BTC 잔액이 부족합니다.")
                
        elif action == "hold":
            print("보유 추천")
            
    except Exception as e:
        print(f"거래 실행 오류: {e}")

def auto_trade():
    """자동매매 메인 로직"""
    try:
        # API 키 설정
        access_key = os.getenv("UPBIT_ACCESS_KEY")
        secret_key = os.getenv("UPBIT_SECRET_KEY")
        
        if not access_key or not secret_key:
            print("API 키가 설정되지 않았습니다.")
            return
        
        # 업비트 객체 생성
        upbit = pyupbit.Upbit(access_key, secret_key)
        
        print("=" * 50)
        print(f"자동매매 실행 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. 현재 투자 상태 조회
        investment_status = get_investment_status(upbit)
        if not investment_status:
            print("투자 상태 조회 실패")
            return
            
        print(f"현재 투자 상태:")
        print(f"  - KRW 잔고: {investment_status['krw_balance']:,.0f}원")
        print(f"  - BTC 잔고: {investment_status['btc_balance']:.8f} BTC")
        print(f"  - BTC 평가금액: {investment_status['btc_value']:,.0f}원")
        print(f"  - 총 자산: {investment_status['total_asset']:,.0f}원")
        if investment_status['btc_avg_buy_price']:
            print(f"  - BTC 평균 매수가: {investment_status['btc_avg_buy_price']:,.0f}원")
        
        # 2. 시장 데이터 수집
        market_data = get_market_data()
        if not market_data:
            print("시장 데이터 수집 실패")
            return
            
        print(f"현재 BTC 가격: {market_data['current_price']:,.0f}원")
        
        # 3. AI 분석 및 추천
        recommendation = get_ai_recommendation(market_data, investment_status)
        if not recommendation:
            print("AI 분석 실패")
            return
            
        print(f"AI 추천:")
        print(f"  - 액션: {recommendation['recommendation']}")
        print(f"  - 신뢰도: {recommendation.get('confidence', 'N/A')}/10")
        print(f"  - 리스크: {recommendation.get('risk_level', 'N/A')}")
        print(f"  - 근거: {recommendation['justification']}")
        
        # 4. 거래 실행
        execute_trade(upbit, recommendation, investment_status)
        
    except Exception as e:
        print(f"자동매매 실행 오류: {e}")

def main():
    """메인 함수"""
    import pyupbit
    
    print("비트코인 자동매매 프로그램 시작")
    print("종료하려면 Ctrl+C를 누르세요.")
    
    try:
        while True:
            auto_trade()
            print(f"30초 후 다시 실행됩니다...")
            print("=" * 50)
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
    except Exception as e:
        print(f"프로그램 오류: {e}")

if __name__ == "__main__":
    main()