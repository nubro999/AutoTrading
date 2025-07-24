# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class TradingConfig:
    """트레이딩 설정"""
    
    # API 키
    UPBIT_ACCESS_KEY = os.getenv("UPBIT_ACCESS_KEY")
    UPBIT_SECRET_KEY = os.getenv("UPBIT_SECRET_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # 거래 설정
    TARGET_COIN = "KRW-BTC"
    MIN_TRADE_AMOUNT = 5000  # 최소 거래 금액 (원)
    MIN_CONFIDENCE = 6  # 최소 신뢰도
    
    # 거래 비율 설정
    TRADE_RATIOS = {
        "high": 0.1,    # 고위험: 10%
        "medium": 0.2,  # 중위험: 20% 
        "low": 0.3      # 저위험: 30%
    }
    
    # 데이터 수집 설정
    DAILY_CANDLE_COUNT = 30
    HOURLY_CANDLE_COUNT = 24
    FNG_DATA_LIMIT = 7  # 공포탐욕지수 조회 일수
    
    # 시스템 설정
    TRADE_INTERVAL = 30  # 거래 주기 (초)
    REQUEST_TIMEOUT = 10  # API 요청 타임아웃 (초)
    
    # 공포탐욕지수 임계값
    FNG_THRESHOLDS = {
        "extreme_fear": 25,
        "fear": 45,
        "neutral": 55,
        "greed": 75
    }
    
    @classmethod
    def validate(cls):
        """설정 유효성 검사"""
        if not cls.UPBIT_ACCESS_KEY or not cls.UPBIT_SECRET_KEY:
            raise ValueError("업비트 API 키가 설정되지 않았습니다.")
        
        if not cls.OPENAI_API_KEY:
            print("경고: OpenAI API 키가 없어 기본 분석을 사용합니다.")
        
        return True