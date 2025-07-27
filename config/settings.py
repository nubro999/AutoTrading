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
    SERPAPI_KEY = os.getenv("SERPAPI_KEY")  # 뉴스 분석용
    
    # 거래 설정
    TARGET_COIN = "AI_AUTO"  # AI가 자동으로 선택
    MIN_TRADE_AMOUNT = 5000  # 최소 거래 금액 (원)
    MIN_CONFIDENCE = 6  # 최소 신뢰도
    
    # AI 완전 자동화 설정
    AI_FULL_AUTO_MODE = True  # AI 완전 자동화 모드 활성화
    AUTO_SELECTION_ENABLED = True  # AI가 자동으로 코인 선택
    SUPPORTED_COINS = [
        "KRW-BTC", "KRW-ETH", "KRW-XRP", "KRW-ADA", "KRW-SOL",
        "KRW-DOGE", "KRW-AVAX", "KRW-DOT", "KRW-MATIC", "KRW-LINK",
        "KRW-UNI", "KRW-LTC", "KRW-BCH", "KRW-ATOM", "KRW-NEAR"
    ]
    
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
    
    # 뉴스 분석 설정
    NEWS_ANALYSIS_ENABLED = bool(SERPAPI_KEY)  # SerpAPI 키가 있을 때만 활성화
    NEWS_WEIGHT = 0.3  # 뉴스 감성의 거래 결정 가중치 (0.0 ~ 1.0)
    
    @classmethod
    def validate(cls):
        """설정 유효성 검사"""
        if not cls.UPBIT_ACCESS_KEY or not cls.UPBIT_SECRET_KEY:
            raise ValueError("업비트 API 키가 설정되지 않았습니다.")
        
        if not cls.OPENAI_API_KEY:
            print("경고: OpenAI API 키가 없어 기본 분석을 사용합니다.")
        
        if not cls.SERPAPI_KEY:
            print("경고: SerpAPI 키가 없어 뉴스 분석을 사용하지 않습니다.")
        
        return True