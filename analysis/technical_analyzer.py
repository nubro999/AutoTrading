# analysis/technical_analyzer.py
import pyupbit
from config.settings import TradingConfig
from data.fear_greed import FearGreedAnalyzer

class TechnicalAnalyzer:
    """기술적 분석 클래스"""
    
    def __init__(self):
        self.target_coin = TradingConfig.TARGET_COIN
        self.fng_analyzer = FearGreedAnalyzer()
    
    def get_fallback_recommendation(self, investment_status, market_data=None):
        """AI 분석 실패 시 기본 추천"""
        try:
            # 간단한 기술적 분석 기반 추천
            df = pyupbit.get_ohlcv(self.target_coin, count=5, interval='day')
            current_price = pyupbit.get_current_price(self.target_coin)
            
            if df is None or current_price is None:
                return self._get_safe_recommendation("데이터 조회 실패")
            
            # 5일 평균가 계산
            avg_price = df['close'].mean()
            
            # 공포탐욕지수 팩터 계산
            fng_factor = self._get_fng_factor(market_data)
            
            # 공포탐욕지수를 반영한 매매 기준 조정
            buy_threshold = 0.98 + fng_factor  # 공포일수록 더 높은 가격에서도 매수
            sell_threshold = 1.05 - fng_factor  # 탐욕일수록 더 낮은 가격에서도 매도
            
            # 매매 결정
            price_ratio = current_price / avg_price
            
            if price_ratio < buy_threshold:
                confidence = 6 if abs(fng_factor) > 0.03 else 5
                return {
                    "recommendation": "buy",
                    "confidence": confidence,
                    "justification": f"현재가가 5일 평균가 대비 하락하고 공포탐욕지수 고려 시 매수 기회",
                    "risk_level": "medium"
                }
            elif price_ratio > sell_threshold:
                confidence = 6 if abs(fng_factor) > 0.03 else 5
                return {
                    "recommendation": "sell", 
                    "confidence": confidence,
                    "justification": f"현재가가 5일 평균가 대비 상승하고 공포탐욕지수 고려 시 수익 실현",
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
            return self._get_safe_recommendation("분석 실패")
    
    def _get_fng_factor(self, market_data):
        """공포탐욕지수 팩터 계산"""
        try:
            if market_data and market_data.get('fear_greed_index'):
                fng_data = market_data['fear_greed_index']
                fng_value = fng_data.get('current_value', 50)
                
                thresholds = TradingConfig.FNG_THRESHOLDS
                
                if fng_value <= thresholds["extreme_fear"]:  # 극도의 공포
                    return 0.05  # 매수 성향 강화
                elif fng_value <= thresholds["fear"]:  # 공포
                    return 0.02  # 매수 성향 증가
                elif fng_value >= thresholds["greed"] + 25:  # 극도의 탐욕
                    return -0.05  # 매도 성향 강화
                elif fng_value >= thresholds["neutral"]:  # 탐욕
                    return -0.02  # 매도 성향 증가
            
            return 0  # 중립
            
        except Exception as e:
            print(f"공포탐욕지수 팩터 계산 오류: {e}")
            return 0
    
    def _get_safe_recommendation(self, reason):
        """안전한 기본 추천"""
        return {
            "recommendation": "hold",
            "confidence": 3,
            "justification": f"{reason}로 인한 안전한 보유 권장",
            "risk_level": "high"
        }
    
    def calculate_moving_average(self, df, period=5):
        """이동평균 계산"""
        try:
            return df['close'].rolling(window=period).mean()
        except Exception as e:
            print(f"이동평균 계산 오류: {e}")
            return None
    
    def calculate_rsi(self, df, period=14):
        """RSI 계산"""
        try:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception as e:
            print(f"RSI 계산 오류: {e}")
            return None