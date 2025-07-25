# data/news_analyzer.py
import re
import requests
from datetime import datetime, timedelta
from config.settings import TradingConfig

class NewsAPI:
    """SerpAPI를 이용한 Google News 데이터 수집"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"
        self.timeout = TradingConfig.REQUEST_TIMEOUT
    
    def get_bitcoin_news(self, limit=10):
        """비트코인 관련 최신 뉴스 수집"""
        try:
            params = {
                "engine": "google_news",
                "q": "bitcoin OR cryptocurrency OR crypto market",
                "gl": "us",
                "hl": "en",
                "api_key": self.api_key,
                "num": limit
            }
            
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_news_results(data)
            else:
                print(f"뉴스 API 오류: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"뉴스 API 요청 오류: {e}")
            return None
        except Exception as e:
            print(f"뉴스 데이터 처리 오류: {e}")
            return None
    
    def get_business_news(self, limit=10):
        """비즈니스/경제 관련 뉴스 수집"""
        try:
            # Business 토픽으로 뉴스 수집
            params = {
                "engine": "google_news",
                "topic_token": "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB",  # Business topic
                "gl": "us", 
                "hl": "en",
                "api_key": self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_news_results(data)
            else:
                print(f"비즈니스 뉴스 API 오류: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"비즈니스 뉴스 수집 오류: {e}")
            return None
    
    def get_technology_news(self, limit=10):
        """기술 관련 뉴스 수집"""
        try:
            params = {
                "engine": "google_news",
                "topic_token": "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB",  # Technology topic
                "gl": "us",
                "hl": "en", 
                "api_key": self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_news_results(data)
            else:
                print(f"기술 뉴스 API 오류: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"기술 뉴스 수집 오류: {e}")
            return None
    
    def _parse_news_results(self, data):
        """뉴스 결과 파싱"""
        try:
            news_results = data.get("news_results", [])
            parsed_news = []
            
            for item in news_results:
                # 메인 뉴스 처리
                if "title" in item and "source" in item:
                    news_item = {
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                        "source": item.get("source", {}).get("name", ""),
                        "link": item.get("link", ""),
                        "date": item.get("date", ""),
                        "type": "main"
                    }
                    parsed_news.append(news_item)
                
                # 하이라이트 뉴스 처리
                if "highlight" in item:
                    highlight = item["highlight"]
                    news_item = {
                        "title": highlight.get("title", ""),
                        "snippet": highlight.get("snippet", ""),
                        "source": highlight.get("source", {}).get("name", ""),
                        "link": highlight.get("link", ""),
                        "date": highlight.get("date", ""),
                        "type": "highlight"
                    }
                    parsed_news.append(news_item)
                
                # 스토리 뉴스 처리
                if "stories" in item:
                    for story in item["stories"][:3]:  # 최대 3개 스토리만
                        news_item = {
                            "title": story.get("title", ""),
                            "snippet": story.get("snippet", ""),
                            "source": story.get("source", {}).get("name", ""),
                            "link": story.get("link", ""),
                            "date": story.get("date", ""),
                            "type": "story"
                        }
                        parsed_news.append(news_item)
            
            return parsed_news[:20]  # 최대 20개 뉴스만 반환
            
        except Exception as e:
            print(f"뉴스 파싱 오류: {e}")
            return []

class NewsAnalyzer:
    """뉴스 감성 분석 및 시장 영향도 분석"""
    
    def __init__(self, serpapi_key=None):
        self.news_api = NewsAPI(serpapi_key) if serpapi_key else None
        self.sentiment_keywords = self._load_sentiment_keywords()
    
    def _load_sentiment_keywords(self):
        """감성 분석용 키워드 정의"""
        return {
            "positive": {
                "strong": ["surge", "soar", "rally", "boom", "breakout", "bullish", "adoption", "breakthrough"],
                "medium": ["rise", "gain", "increase", "growth", "positive", "up", "higher", "recover"],
                "weak": ["slight", "modest", "gradual", "steady"]
            },
            "negative": {
                "strong": ["crash", "plunge", "collapse", "bearish", "ban", "crackdown", "regulation", "hack"],
                "medium": ["fall", "drop", "decline", "down", "lower", "loss", "concern", "worry"],
                "weak": ["caution", "uncertainty", "volatility", "mixed"]
            },
            "bitcoin_specific": {
                "positive": ["halving", "etf approval", "institutional adoption", "mainstream", "legal tender"],
                "negative": ["mining ban", "energy consumption", "volatility", "speculation", "bubble"]
            }
        }
    
    def analyze_news_sentiment(self, news_data):
        """뉴스 감성 분석"""
        if not news_data:
            return None
        
        try:
            sentiment_scores = []
            analyzed_news = []
            
            for news_item in news_data:
                title = news_item.get("title", "").lower()
                snippet = news_item.get("snippet", "").lower()
                text = f"{title} {snippet}"
                
                # 감성 점수 계산
                score = self._calculate_sentiment_score(text)
                sentiment_scores.append(score)
                
                # 분석된 뉴스 아이템
                analyzed_item = {
                    **news_item,
                    "sentiment_score": score,
                    "sentiment": "positive" if score > 0.1 else "negative" if score < -0.1 else "neutral"
                }
                analyzed_news.append(analyzed_item)
            
            # 전체 감성 점수 계산
            if sentiment_scores:
                avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
                
                # 최근 뉴스일수록 가중치 부여
                weighted_sentiment = self._calculate_weighted_sentiment(analyzed_news)
                
                return {
                    "average_sentiment": round(avg_sentiment, 3),
                    "weighted_sentiment": round(weighted_sentiment, 3),
                    "total_news_count": len(analyzed_news),
                    "positive_count": len([n for n in analyzed_news if n["sentiment"] == "positive"]),
                    "negative_count": len([n for n in analyzed_news if n["sentiment"] == "negative"]),
                    "neutral_count": len([n for n in analyzed_news if n["sentiment"] == "neutral"]),
                    "news_items": analyzed_news[:10],  # 상위 10개 뉴스만
                    "market_signal": self._interpret_market_signal(weighted_sentiment)
                }
            
            return None
            
        except Exception as e:
            print(f"뉴스 감성 분석 오류: {e}")
            return None
    
    def _calculate_sentiment_score(self, text):
        """텍스트 감성 점수 계산"""
        try:
            score = 0
            
            # 긍정 키워드 점수
            for strength, keywords in self.sentiment_keywords["positive"].items():
                multiplier = 3 if strength == "strong" else 2 if strength == "medium" else 1
                for keyword in keywords:
                    count = len(re.findall(rf'\b{re.escape(keyword)}\b', text))
                    score += count * multiplier * 0.1
            
            # 부정 키워드 점수
            for strength, keywords in self.sentiment_keywords["negative"].items():
                multiplier = 3 if strength == "strong" else 2 if strength == "medium" else 1
                for keyword in keywords:
                    count = len(re.findall(rf'\b{re.escape(keyword)}\b', text))
                    score -= count * multiplier * 0.1
            
            # 비트코인 특정 키워드
            for sentiment, keywords in self.sentiment_keywords["bitcoin_specific"].items():
                multiplier = 2  # 비트코인 특정 키워드는 가중치 높임
                for keyword in keywords:
                    count = len(re.findall(rf'\b{re.escape(keyword)}\b', text))
                    if sentiment == "positive":
                        score += count * multiplier * 0.15
                    else:
                        score -= count * multiplier * 0.15
            
            # 점수 범위 제한 (-1.0 ~ 1.0)
            return max(-1.0, min(1.0, score))
            
        except Exception as e:
            print(f"감성 점수 계산 오류: {e}")
            return 0
    
    def _calculate_weighted_sentiment(self, analyzed_news):
        """시간 가중치 적용한 감성 점수"""
        try:
            weighted_score = 0
            total_weight = 0
            
            for i, news_item in enumerate(analyzed_news):
                # 최근 뉴스일수록 높은 가중치 (첫 번째부터 순서대로 감소)
                weight = 1.0 / (i + 1)
                weighted_score += news_item["sentiment_score"] * weight
                total_weight += weight
            
            return weighted_score / total_weight if total_weight > 0 else 0
            
        except Exception as e:
            print(f"가중치 감성 점수 계산 오류: {e}")
            return 0
    
    def _interpret_market_signal(self, weighted_sentiment):
        """감성 점수를 시장 신호로 해석"""
        if weighted_sentiment > 0.3:
            return {"signal": "strong_bullish", "strength": "강한 상승", "factor": 0.03}
        elif weighted_sentiment > 0.1:
            return {"signal": "bullish", "strength": "상승", "factor": 0.015}
        elif weighted_sentiment < -0.3:
            return {"signal": "strong_bearish", "strength": "강한 하락", "factor": -0.03}
        elif weighted_sentiment < -0.1:
            return {"signal": "bearish", "strength": "하락", "factor": -0.015}
        else:
            return {"signal": "neutral", "strength": "중립", "factor": 0}
    
    def get_comprehensive_news_analysis(self):
        """종합적인 뉴스 분석"""
        if not self.news_api:
            print("SerpAPI 키가 설정되지 않았습니다.")
            return None
        
        try:
            # 다양한 카테고리 뉴스 수집
            bitcoin_news = self.news_api.get_bitcoin_news(limit=15)
            business_news = self.news_api.get_business_news(limit=10) 
            tech_news = self.news_api.get_technology_news(limit=10)
            
            # 뉴스 통합
            all_news = []
            if bitcoin_news:
                all_news.extend(bitcoin_news)
            if business_news:
                all_news.extend(business_news[:5])  # 비즈니스 뉴스는 5개만
            if tech_news:
                all_news.extend(tech_news[:5])  # 기술 뉴스는 5개만
            
            if not all_news:
                return None
            
            # 중복 제거 (제목 기준)
            seen_titles = set()
            unique_news = []
            for news_item in all_news:
                title = news_item.get("title", "")
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    unique_news.append(news_item)
            
            # 감성 분석 실행
            analysis_result = self.analyze_news_sentiment(unique_news)
            
            if analysis_result:
                analysis_result["data_sources"] = {
                    "bitcoin_news_count": len(bitcoin_news) if bitcoin_news else 0,
                    "business_news_count": len(business_news) if business_news else 0,
                    "tech_news_count": len(tech_news) if tech_news else 0,
                    "total_collected": len(unique_news)
                }
            
            return analysis_result
            
        except Exception as e:
            print(f"종합 뉴스 분석 오류: {e}")
            return None
    
    def get_news_trading_factor(self):
        """뉴스 기반 거래 팩터 반환"""
        try:
            analysis = self.get_comprehensive_news_analysis()
            if not analysis:
                return 0
            
            market_signal = analysis.get("market_signal", {})
            return market_signal.get("factor", 0)
            
        except Exception as e:
            print(f"뉴스 거래 팩터 계산 오류: {e}")
            return 0