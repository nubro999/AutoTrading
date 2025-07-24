# data/market_data.py
import pyupbit
from config.settings import TradingConfig
from data.fear_greed import FearGreedAnalyzer

class MarketDataCollector:
    """시장 데이터 수집 클래스"""
    
    def __init__(self):
        self.target_coin = TradingConfig.TARGET_COIN
        self.daily_count = TradingConfig.DAILY_CANDLE_COUNT
        self.hourly_count = TradingConfig.HOURLY_CANDLE_COUNT
        self.fng_analyzer = FearGreedAnalyzer()
    
    def get_ohlcv_data(self):
        """OHLCV 데이터 수집"""
        try:
            # 일봉 데이터
            daily_df = pyupbit.get_ohlcv(
                self.target_coin, 
                count=self.daily_count, 
                interval='day'
            )
            
            # 시간봉 데이터  
            hourly_df = pyupbit.get_ohlcv(
                self.target_coin, 
                count=self.hourly_count, 
                interval='minute60'
            )
            
            return {
                "daily": daily_df,
                "hourly": hourly_df
            }
            
        except Exception as e:
            print(f"OHLCV 데이터 수집 오류: {e}")
            return None
    
    def get_current_price(self):
        """현재 가격 조회"""
        try:
            return pyupbit.get_current_price(self.target_coin)
        except Exception as e:
            print(f"현재 가격 조회 오류: {e}")
            return None
    
    def get_orderbook(self):
        """호가 정보 조회"""
        try:
            return pyupbit.get_orderbook(ticker=self.target_coin)
        except Exception as e:
            print(f"호가 정보 조회 오류: {e}")
            return None
    
    def get_all_market_data(self):
        """모든 시장 데이터 수집"""
        try:
            # OHLCV 데이터
            ohlcv_data = self.get_ohlcv_data()
            if not ohlcv_data:
                return None
            
            # 현재 가격
            current_price = self.get_current_price()
            if not current_price:
                return None
            
            # 호가 정보
            orderbook = self.get_orderbook()
            
            # 공포탐욕지수
            fear_greed_data = self.fng_analyzer.analyze_trend()
            
            return {
                "daily_ohlcv": ohlcv_data["daily"].to_json(),
                "hourly_ohlcv": ohlcv_data["hourly"].to_json(), 
                "current_price": current_price,
                "orderbook": orderbook,
                "fear_greed_index": fear_greed_data
            }
            
        except Exception as e:
            print(f"시장 데이터 수집 오류: {e}")
            return None
    
    def get_simple_price_data(self, days=5):
        """간단한 가격 데이터 (백업용)"""
        try:
            df = pyupbit.get_ohlcv(self.target_coin, count=days, interval='day')
            current_price = pyupbit.get_current_price(self.target_coin)
            
            return {
                "df": df,
                "current_price": current_price,
                "avg_price": df['close'].mean()
            }
            
        except Exception as e:
            print(f"간단한 가격 데이터 수집 오류: {e}")
            return None