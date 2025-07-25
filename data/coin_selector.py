# data/coin_selector.py
import pyupbit
import requests
from datetime import datetime, timedelta
from config.settings import TradingConfig
from data.news_analyzer import NewsAnalyzer

class CoinSelector:
    """암호화폐 종목 자동 선택 클래스"""
    
    def __init__(self, serpapi_key=None):
        self.news_analyzer = NewsAnalyzer(serpapi_key) if serpapi_key else None
        self.supported_coins = [
            "KRW-BTC", "KRW-ETH", "KRW-XRP", "KRW-ADA", "KRW-SOL",
            "KRW-DOGE", "KRW-AVAX", "KRW-DOT", "KRW-MATIC", "KRW-LINK",
            "KRW-UNI", "KRW-LTC", "KRW-BCH", "KRW-ATOM", "KRW-NEAR"
        ]
    
    def get_coin_market_data(self, coin_symbol, days=7):
        """개별 코인의 시장 데이터 수집"""
        try:
            # 7일간 일봉 데이터
            df = pyupbit.get_ohlcv(coin_symbol, count=days, interval='day')
            if df is None or len(df) < days:
                return None
            
            current_price = pyupbit.get_current_price(coin_symbol)
            if not current_price:
                return None
            
            # 거래량 정보
            volume_24h = df['volume'].iloc[-1]  # 24시간 거래량
            avg_volume = df['volume'].mean()    # 평균 거래량
            
            # 가격 변동률
            price_change_7d = ((current_price - df['close'].iloc[0]) / df['close'].iloc[0]) * 100
            price_change_1d = ((current_price - df['close'].iloc[-2]) / df['close'].iloc[-2]) * 100 if len(df) > 1 else 0
            
            # 변동성 (표준편차)
            volatility = df['close'].pct_change().std() * 100
            
            return {
                "symbol": coin_symbol,
                "current_price": current_price,
                "price_change_1d": price_change_1d,
                "price_change_7d": price_change_7d,
                "volume_24h": volume_24h,
                "avg_volume": avg_volume,
                "volatility": volatility,
                "market_cap_rank": self._get_market_cap_rank(coin_symbol)
            }
            
        except Exception as e:
            print(f"{coin_symbol} 데이터 수집 오류: {e}")
            return None
    
    def _get_market_cap_rank(self, coin_symbol):
        """코인 시가총액 순위 추정 (간단한 매핑)"""
        rank_mapping = {
            "KRW-BTC": 1, "KRW-ETH": 2, "KRW-XRP": 3, "KRW-ADA": 4, "KRW-SOL": 5,
            "KRW-DOGE": 6, "KRW-AVAX": 7, "KRW-DOT": 8, "KRW-MATIC": 9, "KRW-LINK": 10,
            "KRW-UNI": 11, "KRW-LTC": 12, "KRW-BCH": 13, "KRW-ATOM": 14, "KRW-NEAR": 15
        }
        return rank_mapping.get(coin_symbol, 999)
    
    def get_trending_coins_from_news(self):
        """뉴스에서 언급되는 트렌딩 코인 추출"""
        if not self.news_analyzer:
            return []
        
        try:
            # 암호화폐 관련 뉴스 수집
            bitcoin_news = self.news_analyzer.news_api.get_bitcoin_news(limit=20)
            tech_news = self.news_analyzer.news_api.get_technology_news(limit=10)
            
            all_news = []
            if bitcoin_news:
                all_news.extend(bitcoin_news)
            if tech_news:
                # 기술 뉴스 중 암호화폐 관련만 필터링
                crypto_tech_news = [
                    news for news in tech_news 
                    if any(keyword in news.get('title', '').lower() + news.get('snippet', '').lower() 
                          for keyword in ['crypto', 'bitcoin', 'ethereum', 'blockchain', 'defi', 'nft'])
                ]
                all_news.extend(crypto_tech_news)
            
            if not all_news:
                return []
            
            # 코인 이름 매핑
            coin_keywords = {
                "KRW-BTC": ["bitcoin", "btc"],
                "KRW-ETH": ["ethereum", "eth", "ether"],
                "KRW-XRP": ["ripple", "xrp"],
                "KRW-ADA": ["cardano", "ada"],
                "KRW-SOL": ["solana", "sol"],
                "KRW-DOGE": ["dogecoin", "doge"],
                "KRW-AVAX": ["avalanche", "avax"],
                "KRW-DOT": ["polkadot", "dot"],
                "KRW-MATIC": ["polygon", "matic"],
                "KRW-LINK": ["chainlink", "link"],
                "KRW-UNI": ["uniswap", "uni"],
                "KRW-LTC": ["litecoin", "ltc"],
                "KRW-BCH": ["bitcoin cash", "bch"],
                "KRW-ATOM": ["cosmos", "atom"],
                "KRW-NEAR": ["near protocol", "near"]
            }
            
            # 뉴스에서 코인 언급 횟수 카운트
            coin_mentions = {}
            coin_sentiment = {}
            
            for news_item in all_news:
                text = (news_item.get('title', '') + ' ' + news_item.get('snippet', '')).lower()
                
                for coin_symbol, keywords in coin_keywords.items():
                    mention_count = sum(text.count(keyword) for keyword in keywords)
                    if mention_count > 0:
                        coin_mentions[coin_symbol] = coin_mentions.get(coin_symbol, 0) + mention_count
                        
                        # 뉴스 감성도 함께 수집
                        if coin_symbol not in coin_sentiment:
                            coin_sentiment[coin_symbol] = []
                        
                        # 간단한 감성 판단
                        sentiment_score = self.news_analyzer._calculate_sentiment_score(text)
                        coin_sentiment[coin_symbol].append(sentiment_score)
            
            # 언급 횟수와 감성을 조합한 트렌딩 점수 계산
            trending_coins = []
            for coin_symbol, mentions in coin_mentions.items():
                if coin_symbol in coin_sentiment:
                    avg_sentiment = sum(coin_sentiment[coin_symbol]) / len(coin_sentiment[coin_symbol])
                    trending_score = mentions * (1 + avg_sentiment)  # 긍정적 감성일수록 점수 증가
                    
                    trending_coins.append({
                        "symbol": coin_symbol,
                        "mentions": mentions,
                        "avg_sentiment": avg_sentiment,
                        "trending_score": trending_score
                    })
            
            # 트렌딩 점수 순으로 정렬
            trending_coins.sort(key=lambda x: x['trending_score'], reverse=True)
            return trending_coins[:10]  # 상위 10개
            
        except Exception as e:
            print(f"트렌딩 코인 분석 오류: {e}")
            return []
    
    def analyze_coin_performance(self, coin_list=None):
        """코인들의 성과 분석"""
        if not coin_list:
            coin_list = self.supported_coins
        
        coin_analysis = []
        
        for coin_symbol in coin_list:
            market_data = self.get_coin_market_data(coin_symbol)
            if market_data:
                # 성과 점수 계산 (여러 지표 조합)
                performance_score = self._calculate_performance_score(market_data)
                market_data['performance_score'] = performance_score
                coin_analysis.append(market_data)
        
        # 성과 점수 순으로 정렬
        coin_analysis.sort(key=lambda x: x['performance_score'], reverse=True)
        return coin_analysis
    
    def _calculate_performance_score(self, market_data):
        """종합 성과 점수 계산"""
        try:
            score = 0
            
            # 1. 가격 모멘텀 (30%)
            price_1d = market_data['price_change_1d']
            price_7d = market_data['price_change_7d']
            
            # 단기 상승 추세 선호
            if price_1d > 0:
                score += min(price_1d * 2, 20)  # 최대 20점
            if price_7d > 0:
                score += min(price_7d * 1, 10)  # 최대 10점
            
            # 2. 거래량 활성도 (20%)
            volume_ratio = market_data['volume_24h'] / market_data['avg_volume']
            if volume_ratio > 1.5:  # 평균보다 50% 이상 높은 거래량
                score += min((volume_ratio - 1) * 10, 20)
            
            # 3. 변동성 (20%) - 적당한 변동성 선호
            volatility = market_data['volatility']
            if 2 < volatility < 8:  # 적당한 변동성
                score += 20
            elif volatility < 2:  # 너무 낮은 변동성
                score += 5
            else:  # 너무 높은 변동성
                score += max(0, 15 - volatility)
            
            # 4. 시가총액 순위 (15%) - 상위권 코인 선호
            rank = market_data['market_cap_rank']
            if rank <= 3:
                score += 15
            elif rank <= 10:
                score += 10
            elif rank <= 20:
                score += 5
            
            # 5. 안정성 보너스 (15%)
            if market_data['symbol'] in ['KRW-BTC', 'KRW-ETH']:  # 메이저 코인
                score += 15
            elif market_data['symbol'] in ['KRW-XRP', 'KRW-ADA', 'KRW-SOL']:
                score += 10
            
            return round(score, 2)
            
        except Exception as e:
            print(f"성과 점수 계산 오류: {e}")
            return 0
    
    def select_optimal_coin(self):
        """최적의 거래 코인 선택"""
        try:
            print("🔍 최적 코인 선택 분석 중...")
            
            # 1. 기본 성과 분석
            performance_analysis = self.analyze_coin_performance()
            
            # 2. 뉴스 트렌딩 분석
            trending_coins = self.get_trending_coins_from_news()
            
            # 3. 종합 점수 계산
            final_scores = {}
            
            for coin_data in performance_analysis:
                symbol = coin_data['symbol']
                base_score = coin_data['performance_score']
                
                # 뉴스 트렌딩 보너스
                trending_bonus = 0
                for trending in trending_coins:
                    if trending['symbol'] == symbol:
                        # 트렌딩 순위에 따른 보너스 (최대 30점)
                        rank_bonus = max(0, 30 - trending_coins.index(trending) * 3)
                        sentiment_bonus = trending['avg_sentiment'] * 10  # 감성 보너스
                        trending_bonus = rank_bonus + sentiment_bonus
                        break
                
                final_scores[symbol] = {
                    'base_score': base_score,
                    'trending_bonus': trending_bonus,
                    'final_score': base_score + trending_bonus,
                    'coin_data': coin_data
                }
            
            # 최고 점수 코인 선택
            if final_scores:
                best_coin = max(final_scores.items(), key=lambda x: x[1]['final_score'])
                
                result = {
                    'selected_coin': best_coin[0],
                    'final_score': best_coin[1]['final_score'],
                    'base_score': best_coin[1]['base_score'],
                    'trending_bonus': best_coin[1]['trending_bonus'],
                    'coin_data': best_coin[1]['coin_data'],
                    'analysis_summary': {
                        'total_analyzed': len(performance_analysis),
                        'trending_coins_count': len(trending_coins),
                        'top_3_coins': [(k, v['final_score']) for k, v in sorted(final_scores.items(), key=lambda x: x[1]['final_score'], reverse=True)[:3]]
                    }
                }
                
                return result
            
            # 기본값 반환
            return {'selected_coin': 'KRW-BTC', 'reason': '분석 실패로 기본 코인 선택'}
            
        except Exception as e:
            print(f"코인 선택 오류: {e}")
            return {'selected_coin': 'KRW-BTC', 'reason': f'오류로 인한 기본 코인 선택: {e}'}
    
    def print_selection_analysis(self, selection_result):
        """코인 선택 분석 결과 출력"""
        try:
            print("\n" + "="*50)
            print("🎯 최적 코인 선택 결과")
            print("="*50)
            
            selected_coin = selection_result['selected_coin']
            coin_name = selected_coin.replace('KRW-', '')
            
            print(f"🏆 선택된 코인: {coin_name} ({selected_coin})")
            print(f"📊 최종 점수: {selection_result.get('final_score', 0):.2f}점")
            
            if 'base_score' in selection_result:
                print(f"  - 기본 성과: {selection_result['base_score']:.2f}점")
                print(f"  - 뉴스 보너스: {selection_result['trending_bonus']:.2f}점")
            
            if 'coin_data' in selection_result:
                data = selection_result['coin_data']
                print(f"\n📈 코인 정보:")
                print(f"  - 현재가: {data['current_price']:,.0f}원")
                print(f"  - 1일 변동: {data['price_change_1d']:+.2f}%")
                print(f"  - 7일 변동: {data['price_change_7d']:+.2f}%")
                print(f"  - 변동성: {data['volatility']:.2f}%")
                print(f"  - 시총 순위: {data['market_cap_rank']}위")
            
            if 'analysis_summary' in selection_result:
                summary = selection_result['analysis_summary']
                print(f"\n📋 분석 요약:")
                print(f"  - 분석 코인 수: {summary['total_analyzed']}개")
                print(f"  - 트렌딩 코인: {summary['trending_coins_count']}개")
                print(f"  - 상위 3개 코인:")
                for i, (coin, score) in enumerate(summary['top_3_coins'], 1):
                    coin_name = coin.replace('KRW-', '')
                    print(f"    {i}. {coin_name}: {score:.2f}점")
            
        except Exception as e:
            print(f"선택 결과 출력 오류: {e}")