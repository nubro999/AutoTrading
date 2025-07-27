# data/fear_greed.py
import requests
from config.settings import TradingConfig

class FearGreedIndexAPI:
    """공포탐욕지수 API 클래스"""
    
    def __init__(self):
        self.base_url = "https://api.alternative.me/fng/"
        self.timeout = TradingConfig.REQUEST_TIMEOUT
    
    def get_data(self, limit=None):
        """공포탐욕지수 데이터 수집"""
        try:
            limit = limit or TradingConfig.FNG_DATA_LIMIT
            url = f"{self.base_url}?limit={limit}"
            
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('metadata', {}).get('error') is None:
                    return data
            
            print(f"공포탐욕지수 API 오류: {response.status_code}")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"공포탐욕지수 API 요청 오류: {e}")
            return None
        except Exception as e:
            print(f"공포탐욕지수 데이터 처리 오류: {e}")
            return None

class FearGreedAnalyzer:
    """공포탐욕지수 분석 클래스"""
    
    def __init__(self):
        self.api = FearGreedIndexAPI()
        self.thresholds = TradingConfig.FNG_THRESHOLDS
    
    def analyze_trend(self, fng_data=None):
        """공포탐욕지수 트렌드 분석"""
        if not fng_data:
            fng_data = self.api.get_data()
        
        if not fng_data or not fng_data.get('data'):
            return None
        
        try:
            values = [int(item['value']) for item in fng_data['data']]
            classifications = [item['value_classification'] for item in fng_data['data']]
            
            current_value = values[0]
            current_classification = classifications[0]
            
            # 7일 평균 계산
            avg_value = sum(values) / len(values)
            
            # 트렌드 분석 (상승/하락)
            if len(values) >= 3:
                recent_trend = "상승" if values[0] > values[2] else "하락" if values[0] < values[2] else "횡보"
            else:
                recent_trend = "불충분"
            
            # 투자 신호 해석
            market_sentiment, buy_signal_strength = self._interpret_signal(current_value)
            
            return {
                "current_value": current_value,
                "current_classification": current_classification,
                "average_7days": round(avg_value, 1),
                "trend": recent_trend,
                "market_sentiment": market_sentiment,
                "buy_signal_strength": buy_signal_strength,
                "raw_data": fng_data['data'][:3]  # 최근 3일 데이터만
            }
            
        except Exception as e:
            print(f"공포탐욕지수 분석 오류: {e}")
            return None
    
    def _interpret_signal(self, value):
        """공포탐욕지수 값에 따른 신호 해석"""
        if value <= self.thresholds["extreme_fear"]:
            return "극도의 공포 - 매수 기회", "강함"
        elif value <= self.thresholds["fear"]:
            return "공포 - 조심스러운 매수", "보통"
        elif value <= self.thresholds["neutral"]:
            return "중립 - 관망", "약함"
        elif value <= self.thresholds["greed"]:
            return "탐욕 - 조심스러운 매도", "약함"
        else:
            return "극도의 탐욕 - 매도 고려", "없음"
    
    def get_trade_factor(self, fng_data=None):
        """거래 결정을 위한 공포탐욕지수 팩터 반환"""
        if not fng_data:
            analysis = self.analyze_trend()
        else:
            analysis = self.analyze_trend(fng_data)
        
        if not analysis:
            return 0
        
        fng_value = analysis["current_value"]
        
        if fng_value <= self.thresholds["extreme_fear"]:
            return 0.05  # 매수 성향 강화
        elif fng_value <= self.thresholds["fear"]:
            return 0.02  # 매수 성향 증가
        elif fng_value >= self.thresholds["greed"] + 25:  # 극도의 탐욕
            return -0.05  # 매도 성향 강화
        elif fng_value >= self.thresholds["neutral"]:
            return -0.02  # 매도 성향 증가
        
        return 0  # 중립
    