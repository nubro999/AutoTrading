# analysis/ai_master.py
import json
from openai import OpenAI, APIError, RateLimitError
from config.settings import TradingConfig

class AIMasterAnalyzer:
    """AI master analyzer for making comprehensive trading decisions."""
    
    def __init__(self):
        self.client = OpenAI(http_client=None) if TradingConfig.OPENAI_API_KEY else None
        self.system_prompt = self._get_master_system_prompt()
    
    def _get_master_system_prompt(self):
        """Generates the master AI system prompt."""
        return '''You are a cryptocurrency investment expert. You must analyze all data to decide:
1. Which coin to trade
2. Whether to buy, sell, or hold that coin

**Data to Analyze:**
- **Multi-Coin OHLCV**: 30-day daily and 24-hour hourly data for multiple coins
- **News Headlines**: Latest crypto news and sentiment analysis
- **Fear & Greed Index**: Market sentiment indicator (0-100)
- **Investment Status**: Current cash, and holdings for each coin
- **Coin Performance**: Recent performance metrics for each coin

**Analysis Steps:**

**Step 1: Overall Market Analysis**
- Gauge market sentiment with the Fear & Greed Index
- Analyze the overall tone of the news
- Determine the cryptocurrency market trend

**Step 2: Individual Coin Analysis**
Comprehensive evaluation for each coin:
- Technical analysis (OHLCV, moving averages, volume)
- Price momentum (short/medium-term volatility)
- News impact (news related to the coin)
- Market position (market cap rank, liquidity)

**Step 3: Optimal Coin Selection**
Select the most promising coin:
- Upside potential
- Risk-reward ratio
- Alignment with market momentum
- Concordance with news and market sentiment

**Step 4: Trading Decision**
- **Buy**: Strong upward signal, good entry timing
- **Sell**: Downward signal, profit-taking opportunity
- **Hold**: Uncertainty or appropriate to maintain the current position

**Risk Management:**
- Limit investment in a single coin to a maximum of 80%
- Consider selling if a loss exceeds 20%
- Be cautious with extremely high-volatility coins
- Avoid low-volume coins

**Response Format (JSON):**
{
    "market_analysis": {
        "overall_sentiment": "bullish/bearish/neutral",
        "fear_greed_interpretation": "Interpretation of market sentiment",
        "news_impact": "Impact of news on the market",
        "trend_direction": "up/down/sideways"
    },
    "selected_coin": {
        "symbol": "KRW-XXX",
        "name": "Coin Name",
        "selection_reason": "2-3 sentence reason for selection"
    },
    "recommendation": {
        "action": "buy/sell/hold",
        "confidence": 1-10,
        "justification": "3-4 sentence basis for the trade",
        "risk_level": "low/medium/high"
    },
    "analysis_details": {
        "technical_signals": "Summary of technical signals",
        "news_influence": "Influence of news",
        "market_timing": "Market timing analysis",
        "key_factors": ["3-5 key decision factors"]
    },
    "risk_management": {
        "position_size": "Appropriate investment proportion (0.1-0.8)",
        "stop_loss": "Stop-loss criteria (%)",
        "take_profit": "Take-profit criteria (%)"
    }
}'''

    def analyze_and_decide(self, multi_coin_data, investment_status, market_context):
        """Analyzes multiple coins and decides which to trade."""
        if not self.client:
            print("Skipping AI Master analysis due to missing OpenAI API key.")
            return None
        
        try:
            master_data = {
                "market_context": market_context,
                "multi_coin_data": multi_coin_data,
                "investment_status": investment_status
            }
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Analyze the following data to select the best coin and make a trading decision: {json.dumps(master_data, ensure_ascii=False)}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=4096
            )
            
            result = json.loads(response.choices[0].message.content)
            return self._validate_master_response(result)
            
        except (APIError, RateLimitError) as e:
            print(f"OpenAI API error in AI Master: {e}")
        except json.JSONDecodeError as e:
            print(f"Error parsing AI Master response JSON: {e}")
        except Exception as e:
            print(f"An unexpected error occurred in AI Master analysis: {e}")
        return None
    
    def _validate_master_response(self, response):
        """Validates the response from the AI Master."""
        try:
            required_sections = ["market_analysis", "selected_coin", "recommendation"]
            if not all(section in response for section in required_sections):
                missing = [section for section in required_sections if section not in response]
                print(f"AI Master response is missing required sections: {missing}")
                return None
            
            selected_coin = response["selected_coin"]
            if "symbol" not in selected_coin or not selected_coin["symbol"].startswith("KRW-"):
                print(f"Invalid coin symbol in AI Master response: {selected_coin.get('symbol', 'None')}")
                return None
            
            recommendation = response["recommendation"]
            if recommendation.get("action") not in ["buy", "sell", "hold"]:
                print(f"Invalid action in AI Master response: {recommendation.get('action')}")
                return None
            
            if not (1 <= recommendation.get("confidence", 0) <= 10):
                print(f"Invalid confidence in AI Master response: {recommendation.get('confidence')}")
                return None
            
            response.setdefault("risk_management", {
                "position_size": 0.3,
                "stop_loss": 15,
                "take_profit": 25
            })
            
            return response
            
        except (TypeError, KeyError) as e:
            print(f"Error validating AI Master response structure: {e}")
            return None
    
    def get_fallback_decision(self, multi_coin_data, investment_status):
        """Provides a fallback decision if the AI analysis fails."""
        try:
            return {
                "market_analysis": {
                    "overall_sentiment": "neutral",
                    "fear_greed_interpretation": "Neutral due to lack of data",
                    "news_impact": "Analysis unavailable",
                    "trend_direction": "sideways"
                },
                "selected_coin": {
                    "symbol": "KRW-BTC",
                    "name": "Bitcoin",
                    "selection_reason": "Default to safe coin due to AI analysis failure"
                },
                "recommendation": {
                    "action": "hold",
                    "confidence": 3,
                    "justification": "Conservative hold recommended due to analysis failure",
                    "risk_level": "high"
                },
                "analysis_details": {
                    "technical_signals": "Unavailable",
                    "news_influence": "Unavailable",
                    "market_timing": "Uncertain",
                    "key_factors": ["AI analysis failed", "Conservative approach", "Risk aversion"]
                },
                "risk_management": {
                    "position_size": 0.1,
                    "stop_loss": 10,
                    "take_profit": 15
                }
            }
        except Exception as e:
            print(f"Error in fallback decision logic: {e}")
            return None