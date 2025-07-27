import json
from openai import OpenAI, APIError, RateLimitError
from config.settings import TradingConfig

class AIAnalyzer:
    """AI analysis class with improved error handling."""
    
    def __init__(self):
        self.client = OpenAI() if TradingConfig.OPENAI_API_KEY else None
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self):
        """Generates the system prompt for the AI."""
        return '''You are a professional Bitcoin trader. Analyze the provided data to make a trading decision.

Data to analyze:
1. daily_ohlcv: 30-day daily data (OHLCV)
2. hourly_ohlcv: 24-hour hourly data (OHLCV) 
3. current_price: Current Bitcoin price
4. orderbook: Bid/ask price information
5. investment_status: Current investment status (cash, BTC quantity, average purchase price, etc.)
6. fear_greed_index: Fear and Greed Index data (current_value, trend, market_sentiment, etc.)

Analysis elements:
- Price trend (short/long term)
- Moving average patterns
- Technical indicators like RSI, MACD
- Volume analysis
- Support/resistance level analysis
- Order book analysis (buy/sell pressure)
- Risk management relative to the current position
- **Fear and Greed Index Analysis**: 
  * 0-25: Extreme Fear (strong buy signal)
  * 26-45: Fear (consider buying)
  * 46-55: Neutral (wait and see)
  * 56-75: Greed (consider selling)  
  * 76-100: Extreme Greed (strong sell signal)
  * Compare 7-day average with the current value
  * Recent trend direction

Please provide the response in JSON format only:
{
    "recommendation": "buy" | "sell" | "hold",
    "confidence": 1-10 (confidence level),
    "justification": "1-2 sentence explanation",
    "risk_level": "low" | "medium" | "high"
} '''
    
    def analyze(self, market_data, investment_status, selected_coin_info=None):
        """Performs trade analysis using AI, with robust error handling."""
        if not self.client:
            print("Skipping AI analysis because OpenAI API key is missing.")
            return None
        
        try:
            analysis_data = self._prepare_analysis_data(market_data, investment_status, selected_coin_info)
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Analyze the following data and provide a trading recommendation in JSON format: {json.dumps(analysis_data, ensure_ascii=False)}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=1024
            )
            
            result = json.loads(response.choices[0].message.content)
            return self._validate_response(result)
            
        except (APIError, RateLimitError) as e:
            print(f"OpenAI API error: {e}")
        except json.JSONDecodeError as e:
            print(f"Error parsing AI response JSON: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during AI analysis: {e}")
        return None
    
    def _prepare_analysis_data(self, market_data, investment_status, selected_coin_info):
        """Prepares the data payload for the AI analysis."""
        analysis_data = {
            "market_data": market_data,
            "investment_status": investment_status,
            "selected_coin": selected_coin_info
        }
        news_headlines = self._extract_news_headlines(market_data)
        if news_headlines:
            analysis_data["news_headlines"] = news_headlines
        return analysis_data

    def _extract_news_headlines(self, market_data):
        """Extracts and formats news headlines from market data."""
        try:
            news_analysis = market_data.get('news_analysis')
            if not news_analysis or not news_analysis.get('news_items'):
                return None
            
            headlines = [
                {
                    "title": item.get('title', ''),
                    "source": item.get('source', ''),
                    "sentiment": item.get('sentiment', 'neutral'),
                    "sentiment_score": item.get('sentiment_score', 0)
                }
                for item in news_analysis['news_items'][:10] if item.get('title')
            ]
            
            return {
                "headlines": headlines,
                "overall_sentiment": news_analysis.get('weighted_sentiment', 0),
                "market_signal": news_analysis.get('market_signal', {}),
                "summary": f"{len(headlines)} news items analyzed - Positive: {news_analysis.get('positive_count', 0)}, Negative: {news_analysis.get('negative_count', 0)}"
            }
        except Exception as e:
            print(f"Error extracting news headlines: {e}")
            return None
    
    def _validate_response(self, response):
        """Validates the structure and values of the AI's response."""
        try:
            required_fields = ["recommendation", "confidence", "justification", "risk_level"]
            if not all(field in response for field in required_fields):
                missing = [field for field in required_fields if field not in response]
                print(f"AI response is missing required fields: {missing}")
                return None
            
            if response["recommendation"] not in ["buy", "sell", "hold"]:
                print(f"Invalid recommendation value: {response['recommendation']}")
                return None
            
            if not isinstance(response["confidence"], (int, float)) or not (1 <= response["confidence"] <= 10):
                print(f"Invalid confidence value: {response['confidence']}")
                return None
            
            if response["risk_level"] not in ["low", "medium", "high"]:
                print(f"Invalid risk level: {response['risk_level']}")
                return None
            
            response.setdefault("news_impact", "none")
            response.setdefault("key_factors", [])
            
            return response
        except (TypeError, KeyError) as e:
            print(f"Error validating AI response structure: {e}")
            return None
    
    def get_recommendation(self, market_data, investment_status, selected_coin_info=None):
        """Gets a trading recommendation, falling back to technical analysis on AI failure."""
        ai_result = self.analyze(market_data, investment_status, selected_coin_info)
        if ai_result:
            return ai_result
        
        print("AI analysis failed. Falling back to technical analysis.")
        from analysis.technical_analyzer import TechnicalAnalyzer
        
        tech_analyzer = TechnicalAnalyzer()
        return tech_analyzer.get_fallback_recommendation(investment_status, market_data)