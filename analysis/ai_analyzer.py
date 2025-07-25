
import json
from openai import OpenAI
from config.settings import TradingConfig

class AIAnalyzer:
    """AI 분석 클래스"""
    
    def __init__(self):
        self.client = OpenAI() if TradingConfig.OPENAI_API_KEY else None
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self):
        """시스템 프롬프트 생성"""
        return '''당신은 전문 비트코인 트레이더입니다. 제공된 데이터를 분석하여 매매 결정을 내리세요.

분석할 데이터:
1. daily_ohlcv: 30일 일봉 데이터 (OHLCV)
2. hourly_ohlcv: 24시간 시간봉 데이터 (OHLCV) 
3. current_price: 현재 비트코인 가격
4. orderbook: 매수/매도 호가 정보
5. investment_status: 현재 투자 상태 (보유 현금, BTC 수량, 평균 매수가 등)
6. fear_greed_index: 공포탐욕지수 데이터 (current_value, trend, market_sentiment 등)

분석 요소:
- 가격 트렌드 (단기/장기)
- 이동평균선 패턴
- RSI, MACD 등 기술적 지표
- 거래량 분석
- 지지/저항선 분석
- 호가창 분석 (매수/매도 압력)
- 현재 포지션 대비 리스크 관리
- **공포탐욕지수 분석**: 
  * 0-25: 극도의 공포 (강한 매수 신호)
  * 26-45: 공포 (매수 고려)
  * 46-55: 중립 (관망)
  * 56-75: 탐욕 (매도 고려)  
  * 76-100: 극도의 탐욕 (강한 매도 신호)
  * 7일 평균과 현재값 비교
  * 최근 트렌드 방향성

응답은 반드시 JSON 형식으로 제공해주세요:
{
    "recommendation": "buy" | "sell" | "hold",
    "confidence": 1-10 (확신도),
    "justification": "1-2문장 설명",
    "risk_level": "low" | "medium" | "high"
}'''
    
    def analyze(self, market_data, investment_status, selected_coin_info=None):
        """AI를 통한 매매 분석"""
        if not self.client:
            print("OpenAI API 키가 없어 AI 분석을 건너뜁니다.")
            return None
        
        try:
            # AI에게 제공할 데이터 구성
            analysis_data = {
                "market_data": market_data,
                "investment_status": investment_status,
                "selected_coin": selected_coin_info
            }
            
            # 뉴스 헤드라인 추출 및 정리
            news_headlines = self._extract_news_headlines(market_data)
            if news_headlines:
                analysis_data["news_headlines"] = news_headlines
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
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
            return self._validate_response(result)
            
        except json.JSONDecodeError as e:
            print(f"AI 응답 JSON 파싱 오류: {e}")
            return None
        except Exception as e:
            print(f"AI 분석 오류: {e}")
            return None
    
    def _extract_news_headlines(self, market_data):
        """뉴스 데이터에서 헤드라인 추출"""
        try:
            news_analysis = market_data.get('news_analysis')
            if not news_analysis or not news_analysis.get('news_items'):
                return None
            
            headlines = []
            for news_item in news_analysis['news_items'][:10]:  # 상위 10개만
                headline_info = {
                    "title": news_item.get('title', ''),
                    "source": news_item.get('source', ''),
                    "sentiment": news_item.get('sentiment', 'neutral'),
                    "sentiment_score": news_item.get('sentiment_score', 0)
                }
                if headline_info["title"]:
                    headlines.append(headline_info)
            
            return {
                "headlines": headlines,
                "overall_sentiment": news_analysis.get('weighted_sentiment', 0),
                "market_signal": news_analysis.get('market_signal', {}),
                "summary": f"{len(headlines)}개 뉴스 분석 - 긍정: {news_analysis.get('positive_count', 0)}개, 부정: {news_analysis.get('negative_count', 0)}개"
            }
            
        except Exception as e:
            print(f"뉴스 헤드라인 추출 오류: {e}")
            return None
    
    def _validate_response(self, response):
        """AI 응답 유효성 검사"""
        try:
            # 필수 필드 확인
            required_fields = ["recommendation", "confidence", "justification", "risk_level"]
            for field in required_fields:
                if field not in response:
                    print(f"AI 응답에 '{field}' 필드가 없습니다.")
                    return None
            
            # 값 유효성 검사
            if response["recommendation"] not in ["buy", "sell", "hold"]:
                print(f"잘못된 추천 값: {response['recommendation']}")
                return None
            
            if not isinstance(response["confidence"], (int, float)) or not (1 <= response["confidence"] <= 10):
                print(f"잘못된 신뢰도 값: {response['confidence']}")
                return None
            
            if response["risk_level"] not in ["low", "medium", "high"]:
                print(f"잘못된 리스크 레벨: {response['risk_level']}")
                return None
            
            # 선택적 필드 기본값 설정
            if "news_impact" not in response:
                response["news_impact"] = "none"
            if "key_factors" not in response:
                response["key_factors"] = []
            
            return response
            
        except Exception as e:
            print(f"AI 응답 검증 오류: {e}")
            return None
    
    def get_recommendation(self, market_data, investment_status, selected_coin_info=None):
        """매매 추천 조회 (AI 또는 백업 분석)"""
        # AI 분석 시도
        ai_result = self.analyze(market_data, investment_status, selected_coin_info)
        if ai_result:
            return ai_result
        
        # AI 실패 시 백업 분석 사용  
        print("AI 분석 실패로 기본 분석을 사용합니다.")
        from analysis.technical_analyzer import TechnicalAnalyzer
        
        tech_analyzer = TechnicalAnalyzer()
        return tech_analyzer.get_fallback_recommendation(investment_status, market_data)