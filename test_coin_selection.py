# test_coin_selection.py - 코인 자동 선택 테스트 스크립트

import os
from dotenv import load_dotenv
from data.coin_selector import CoinSelector

load_dotenv()

def test_coin_selection():
    """코인 자동 선택 기능 테스트"""
    
    print("🚀 코인 자동 선택 시스템 테스트")
    print("=" * 50)
    
    # SerpAPI 키 확인
    serpapi_key = os.getenv("SERPAPI_KEY")
    if not serpapi_key:
        print("⚠️ SerpAPI 키가 없어 뉴스 분석 없이 진행합니다.")
    
    # 코인 선택기 초기화
    selector = CoinSelector(serpapi_key)
    
    # 1. 기본 성과 분석 테스트
    print("\n1️⃣ 코인 성과 분석 테스트...")
    performance_analysis = selector.analyze_coin_performance()
    
    if performance_analysis:
        print("\n📊 상위 5개 코인 성과:")
        for i, coin_data in enumerate(performance_analysis[:5], 1):
            symbol = coin_data['symbol'].replace('KRW-', '')
            print(f"{i}. {symbol}: {coin_data['performance_score']:.2f}점")
            print(f"   1일 변동: {coin_data['price_change_1d']:+.2f}%, 7일 변동: {coin_data['price_change_7d']:+.2f}%")
            print(f"   변동성: {coin_data['volatility']:.2f}%, 시총순위: {coin_data['market_cap_rank']}위")
    else:
        print("❌ 성과 분석 실패")
    
    # 2. 뉴스 트렌딩 분석 테스트 (SerpAPI 키가 있는 경우)
    if serpapi_key:
        print("\n2️⃣ 뉴스 트렌딩 분석 테스트...")
        trending_coins = selector.get_trending_coins_from_news()
        
        if trending_coins:
            print("\n📰 뉴스 트렌딩 코인:")
            for i, trending in enumerate(trending_coins[:5], 1):
                symbol = trending['symbol'].replace('KRW-', '')
                print(f"{i}. {symbol}: 언급 {trending['mentions']}회, 감성 {trending['avg_sentiment']:+.3f}")
        else:
            print("❌ 트렌딩 분석 실패 또는 데이터 없음")
    
    # 3. 최종 코인 선택 테스트
    print("\n3️⃣ 최적 코인 선택 테스트...")
    selection_result = selector.select_optimal_coin()
    
    if selection_result:
        selector.print_selection_analysis(selection_result)
    else:
        print("❌ 코인 선택 실패")
    
    print("\n✅ 코인 선택 테스트 완료!")

def test_individual_coin_analysis():
    """개별 코인 분석 테스트"""
    
    print("\n🔍 개별 코인 분석 테스트")
    print("=" * 30)
    
    selector = CoinSelector()
    test_coins = ["KRW-BTC", "KRW-ETH", "KRW-XRP"]
    
    for coin_symbol in test_coins:
        print(f"\n📈 {coin_symbol.replace('KRW-', '')} 분석:")
        
        market_data = selector.get_coin_market_data(coin_symbol)
        if market_data:
            print(f"  현재가: {market_data['current_price']:,.0f}원")
            print(f"  1일 변동: {market_data['price_change_1d']:+.2f}%")
            print(f"  7일 변동: {market_data['price_change_7d']:+.2f}%")
            print(f"  변동성: {market_data['volatility']:.2f}%")
            print(f"  24시간 거래량: {market_data['volume_24h']:,.0f}")
            print(f"  성과 점수: {selector._calculate_performance_score(market_data):.2f}점")
        else:
            print("  ❌ 데이터 수집 실패")

def main():
    """메인 함수"""
    
    print("🎯 선택하세요:")
    print("1. 전체 코인 선택 테스트")
    print("2. 개별 코인 분석 테스트")
    print("3. 모든 테스트")
    
    choice = input("\n입력 (1-3): ").strip()
    
    if choice == "1":
        test_coin_selection()
    elif choice == "2":
        test_individual_coin_analysis()
    elif choice == "3":
        test_individual_coin_analysis()
        test_coin_selection()
    else:
        print("잘못된 선택입니다.")

if __name__ == "__main__":
    main()