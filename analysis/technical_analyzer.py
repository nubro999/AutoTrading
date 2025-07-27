# analysis/technical_analyzer.py
import pyupbit
from config.settings import TradingConfig
from data.fear_greed import FearGreedAnalyzer

class TechnicalAnalyzer:
    """A class for performing technical analysis with improved error handling."""
    
    def __init__(self):
        self.target_coin = TradingConfig.TARGET_COIN
        self.fng_analyzer = FearGreedAnalyzer()
    
    def get_fallback_recommendation(self, investment_status, market_data=None):
        """Provides a fallback recommendation when AI analysis fails."""
        try:
            df = pyupbit.get_ohlcv(self.target_coin, count=5, interval='day')
            current_price = pyupbit.get_current_price(self.target_coin)
            
            if df is None or current_price is None:
                return self._get_safe_recommendation("Failed to retrieve data")
            
            avg_price = df['close'].mean()
            fng_factor = self._get_fng_factor(market_data)
            
            buy_threshold = 0.98 + fng_factor
            sell_threshold = 1.05 - fng_factor
            
            price_ratio = current_price / avg_price
            
            if price_ratio < buy_threshold:
                return self._create_recommendation("buy", 6 if abs(fng_factor) > 0.03 else 5, "Price is below the 5-day average, considering the Fear & Greed Index.", "medium")
            elif price_ratio > sell_threshold:
                return self._create_recommendation("sell", 6 if abs(fng_factor) > 0.03 else 5, "Price is above the 5-day average, considering the Fear & Greed Index.", "medium")
            else:
                return self._create_recommendation("hold", 6, "Price is within a stable range.", "low")
                
        except pyupbit.errors.UpbitError as e:
            print(f"Upbit API error in fallback analysis: {e}")
        except Exception as e:
            print(f"Fallback analysis failed: {e}")
        return self._get_safe_recommendation("Analysis failed")
    
    def _get_fng_factor(self, market_data):
        """Calculates a factor based on the Fear & Greed Index."""
        try:
            if market_data and market_data.get('fear_greed_index'):
                fng_value = market_data['fear_greed_index'].get('current_value', 50)
                thresholds = TradingConfig.FNG_THRESHOLDS
                
                if fng_value <= thresholds["extreme_fear"]:
                    return 0.05
                elif fng_value <= thresholds["fear"]:
                    return 0.02
                elif fng_value >= thresholds["greed"] + 25:
                    return -0.05
                elif fng_value >= thresholds["neutral"]:
                    return -0.02
            return 0
        except (TypeError, KeyError) as e:
            print(f"Error calculating F&G factor: {e}")
            return 0
    
    def _create_recommendation(self, action, confidence, justification, risk_level):
        """Creates a recommendation dictionary."""
        return {
            "recommendation": action,
            "confidence": confidence,
            "justification": justification,
            "risk_level": risk_level
        }

    def _get_safe_recommendation(self, reason):
        """Returns a safe 'hold' recommendation."""
        return self._create_recommendation("hold", 3, f"Safe hold recommended due to: {reason}", "high")
    
    def calculate_moving_average(self, df, period=5):
        """Calculates the moving average."""
        try:
            return df['close'].rolling(window=period).mean()
        except (TypeError, KeyError) as e:
            print(f"Error calculating moving average: {e}")
            return None
    
    def calculate_rsi(self, df, period=14):
        """Calculates the Relative Strength Index (RSI)."""
        try:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        except (TypeError, KeyError, ZeroDivisionError) as e:
            print(f"Error calculating RSI: {e}")
            return None