# test_ai_full_auto.py - AI 완전 자동화 시스템 테스트

import os
from dotenv import load_dotenv
from data.multi_coin_collector import MultiCoinDataCollector
from analysis.ai_master import AIMasterAnalyzer

load_dotenv()

def test_data_collection():
    """다중 코인 데이터 수집 테스트"""
    print("🔍 다중 코인 데이터 수집 테스트")
    print("=" * 40)
    
    collector = MultiCoinDataCollector()
    
    # 종합 시장 데이터 수집
    comprehensive_data = collector.get_comprehensive_market_data()
    
    if comprehensive_data:
        collector.print_market_summary(comprehensive_data)
        
        # 수집된 코인 개수 확인
        coins_data = comprehensive_data["coins_data"]
        print(f"\n✅ 총 {len(coins_data)}개 코인 데이터 수집 성공")
        
        # 샘플 코인 데이터 출력
        sample_coin = list(coins_data.keys())[0]
        sample_data = coins_data[sample_coin]
        
        print(f"\n📊 샘플 데이터 ({sample_coin.replace('KRW-', '')}):")
        print(f"   현재가: {sample_data['current_price']:,.0f}원")
        print(f"   1일 변동: {sample_data['price_changes']['1d']:+.2f}%")
        print(f"   7일 변동: {sample_data['price_changes']['7d']:+.2f}%")
        print(f"   RSI: {sample_data['technical_indicators']['rsi']:.1f}")
        print(f"   변동성: {sample_data['technical_indicators']['volatility']:.2f}%")
        
        return comprehensive_data
    else:
        print("❌ 데이터 수집 실패")
        return None

def test_ai_master_analysis(comprehensive_data=None):
    """AI 마스터 분석 테스트"""
    print("\n🧠 AI 마스터 분석 테스트")
    print("=" * 40)
    
    # OpenAI API 키 확인
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ OpenAI API 키가 설정되지 않았습니다.")
        print("1. OpenAI 계정에서 API 키 발급")
        print("2. .env 파일에 OPENAI_API_KEY=your_api_key 추가")
        return
    
    # 데이터가 없으면 수집
    if not comprehensive_data:
        collector = MultiCoinDataCollector()
        comprehensive_data = collector.get_comprehensive_market_data()
        
        if not comprehensive_data:
            print("❌ 시장 데이터 수집 실패")
            return
    
    # 가상의 투자 상태 생성 (테스트용)
    investment_status = {
        "krw_balance": 1000000,  # 100만원
        "total_coin_value": 0,
        "total_asset": 1000000,
        "coin_holdings": {},
        "portfolio_distribution": {
            "krw_ratio": 1.0,
            "coin_ratio": 0.0
        }
    }
    
    # AI 마스터 분석 실행
    ai_master = AIMasterAnalyzer()
    ai_decision = ai_master.analyze_and_decide(
        comprehensive_data["coins_data"],
        investment_status,
        comprehensive_data["market_context"]
    )
    
    if ai_decision:
        print("\n🎯 AI 마스터 분석 결과:")
        print("=" * 30)
        
        # 시장 분석
        market_analysis = ai_decision["market_analysis"]
        print(f"📊 전체 시장 심리: {market_analysis['overall_sentiment']}")
        print(f"😱 공포탐욕 해석: {market_analysis['fear_greed_interpretation']}")
        print(f"📰 뉴스 영향: {market_analysis['news_impact']}")
        print(f"📈 트렌드: {market_analysis['trend_direction']}")
        
        # 선택된 코인
        selected_coin = ai_decision["selected_coin"]
        print(f"\n🏆 AI 선택 코인: {selected_coin['symbol'].replace('KRW-', '')}")
        print(f"💡 선택 이유: {selected_coin['selection_reason']}")
        
        # 매매 결정
        recommendation = ai_decision["recommendation"]
        action_emoji = "🟢" if recommendation["action"] == "buy" else "🔴" if recommendation["action"] == "sell" else "🟡"
        print(f"\n{action_emoji} AI 결정: {recommendation['action'].upper()}")
        print(f"🎯 신뢰도: {recommendation['confidence']}/10")
        print(f"⚖️ 리스크: {recommendation['risk_level']}")
        print(f"📝 근거: {recommendation['justification']}")
        
        # 리스크 관리
        if "risk_management" in ai_decision:
            risk_mgmt = ai_decision["risk_management"]
            print(f"\n🛡️ 리스크 관리:")
            print(f"   투자 비중: {float(risk_mgmt['position_size']):.1%}")
            print(f"   손절 기준: {risk_mgmt['stop_loss']}%")
            print(f"   익절 기준: {risk_mgmt['take_profit']}%")
        
        print("\n✅ AI 마스터 분석 완료!")
        return ai_decision
    else:
        print("❌ AI 마스터 분석 실패")
        return None

def test_full_simulation():
    """완전 시뮬레이션 테스트"""
    print("\n🎮 AI 완전 자동화 시뮬레이션")
    print("=" * 40)
    
    # 1단계: 데이터 수집
    print("1️⃣ 시장 데이터 수집...")
    comprehensive_data = test_data_collection()
    
    if not comprehensive_data:
        return
    
    # 2단계: AI 분석
    print("\n2️⃣ AI 마스터 분석...")
    ai_decision = test_ai_master_analysis(comprehensive_data)
    
    if not ai_decision:
        return
    
    # 3단계: 실행 시뮬레이션
    print("\n3️⃣ 거래 실행 시뮬레이션...")
    
    selected_coin = ai_decision["selected_coin"]["symbol"]
    action = ai_decision["recommendation"]["action"]
    confidence = ai_decision["recommendation"]["confidence"]
    position_size = ai_decision.get("risk_management", {}).get("position_size", 0.3)
    
    print(f"📊 선택된 코인: {selected_coin.replace('KRW-', '')}")
    print(f"🎯 실행할 액션: {action.upper()}")
    print(f"💪 신뢰도: {confidence}/10")
    print(f"💰 투자 비중: {float(position_size):.1%}")
    
    if action == "buy":
        simulated_amount = 1000000 * float(position_size)  # 100만원의 30%
        print(f"💵 시뮬레이션 매수: {simulated_amount:,.0f}원")
    elif action == "sell":
        print(f"💵 시뮬레이션 매도: 보유량의 {float(position_size):.1%}")
    else:
        print(f"📌 보유 유지")
    
    print("\n🎉 시뮬레이션 완료!")

def main():
    """메인 함수"""
    print("🤖 AI 완전 자동화 시스템 테스트")
    print("=" * 50)
    
    print("테스트 선택:")
    print("1. 데이터 수집 테스트")
    print("2. AI 분석 테스트")
    print("3. 완전 시뮬레이션 테스트")
    
    choice = input("\n선택하세요 (1-3): ").strip()
    
    if choice == "1":
        test_data_collection()
    elif choice == "2":
        test_ai_master_analysis()
    elif choice == "3":
        test_full_simulation()
    else:
        print("잘못된 선택입니다.")

if __name__ == "__main__":
    main()