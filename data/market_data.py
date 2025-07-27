# data/market_data.py
import pyupbit
import time
from config.settings import TradingConfig
from data.fear_greed import FearGreedAnalyzer
from data.news_analyzer import NewsAnalyzer

class MarketDataCollector:
    """A class for collecting market data, with caching for current price."""
    
    def __init__(self, target_coin=None):
        self.target_coin = target_coin or TradingConfig.TARGET_COIN
        self.daily_count = TradingConfig.DAILY_CANDLE_COUNT
        self.hourly_count = TradingConfig.HOURLY_CANDLE_COUNT
        self.fng_analyzer = FearGreedAnalyzer()
        self.news_analyzer = NewsAnalyzer(TradingConfig.SERPAPI_KEY) if TradingConfig.NEWS_ANALYSIS_ENABLED else None
        
        # Cache for current price to avoid redundant API calls
        self._price_cache = {"price": None, "timestamp": 0}

    def get_current_price(self, coin_symbol=None, force_refresh=False):
        """Retrieves the current price, using a cache to avoid redundant API calls."""
        target = coin_symbol or self.target_coin
        
        # Check cache first
        cache_is_valid = (time.time() - self._price_cache["timestamp"]) < 5 # 5-second cache
        if not force_refresh and self._price_cache["price"] is not None and cache_is_valid:
            return self._price_cache["price"]

        try:
            current_price = pyupbit.get_current_price(target)
            if current_price:
                # Update cache
                self._price_cache["price"] = current_price
                self._price_cache["timestamp"] = time.time()
            return current_price
        except Exception as e:
            print(f"Error fetching current price: {e}")
            return self._price_cache["price"] # Return cached price on error if available
    
    def get_ohlcv_data(self, coin_symbol=None):
        """OHLCV 데이터 수집"""
        try:
            target = coin_symbol or self.target_coin
            
            # 일봉 데이터
            daily_df = pyupbit.get_ohlcv(
                target, 
                count=self.daily_count, 
                interval='day'
            )
            
            # 시간봉 데이터  
            hourly_df = pyupbit.get_ohlcv(
                target, 
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
    
    def get_current_price(self, coin_symbol=None):
        """현재 가격 조회"""
        try:
            target = coin_symbol or self.target_coin
            return pyupbit.get_current_price(target)
        except Exception as e:
            print(f"현재 가격 조회 오류: {e}")
            return None
    
    def get_orderbook(self, coin_symbol=None):
        """호가 정보 조회"""
        try:
            target = coin_symbol or self.target_coin
            return pyupbit.get_orderbook(ticker=target)
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
            
            # 뉴스 분석 (활성화된 경우에만)
            news_analysis = None
            if self.news_analyzer:
                print("뉴스 분석 중...")
                news_analysis = self.news_analyzer.get_comprehensive_news_analysis()
            
            return {
                "daily_ohlcv": ohlcv_data["daily"].to_json(),
                "hourly_ohlcv": ohlcv_data["hourly"].to_json(), 
                "current_price": current_price,
                "orderbook": orderbook,
                "fear_greed_index": fear_greed_data,
                "news_analysis": news_analysis
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