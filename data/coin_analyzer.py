# data/coin_analyzer.py
import pyupbit
from concurrent.futures import ThreadPoolExecutor, as_completed
from config.settings import TradingConfig
from data.news_analyzer import NewsAnalyzer

class CoinAnalyzer:
    """A class for analyzing and selecting coins based on market data and news."""

    def __init__(self, serpapi_key=None):
        self.supported_coins = TradingConfig.SUPPORTED_COINS
        self.news_analyzer = NewsAnalyzer(serpapi_key) if serpapi_key else None

    def get_comprehensive_coin_data(self):
        """Collects and analyzes data for all supported coins in parallel."""
        print(f"Analyzing {len(self.supported_coins)} coins...")
        analyzed_coins = {}
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_coin = {executor.submit(self.analyze_coin, coin): coin for coin in self.supported_coins}
            for future in as_completed(future_to_coin):
                coin_symbol = future_to_coin[future]
                try:
                    data = future.result()
                    if data:
                        analyzed_coins[coin_symbol] = data
                except Exception as e:
                    print(f"Error analyzing {coin_symbol}: {e}")
        
        return {
            "coins_data": analyzed_coins,
            "market_context": {
                "trending_coins": self.get_trending_coins_from_news()
            }
        }

    def analyze_coin(self, coin_symbol):
        """Analyzes a single coin, calculating performance metrics."""
        try:
            df = pyupbit.get_ohlcv(coin_symbol, count=30, interval='day')
            if df is None or len(df) < 30:
                return None

            current_price = pyupbit.get_current_price(coin_symbol)
            if not current_price:
                return None

            # Performance metrics
            price_change_1d = ((current_price - df['close'].iloc[-2]) / df['close'].iloc[-2]) * 100
            price_change_7d = ((current_price - df['close'].iloc[-8]) / df['close'].iloc[-8]) * 100
            volatility = df['close'].pct_change().std() * 100
            volume_24h = df['volume'].iloc[-1]
            avg_volume = df['volume'].mean()

            performance_score = self._calculate_performance_score(
                price_change_1d, price_change_7d, volume_24h, avg_volume, volatility, coin_symbol
            )

            return {
                "symbol": coin_symbol,
                "current_price": current_price,
                "price_change_1d": price_change_1d,
                "price_change_7d": price_change_7d,
                "volume_24h": volume_24h,
                "avg_volume": avg_volume,
                "volatility": volatility,
                "performance_score": performance_score
            }
        except Exception as e:
            print(f"Failed to analyze {coin_symbol}: {e}")
            return None

    def _calculate_performance_score(self, price_1d, price_7d, volume_24h, avg_volume, volatility, symbol):
        """Calculates a weighted performance score for a coin."""
        score = 0
        # Momentum (40%)
        score += min(price_1d * 2, 25) if price_1d > 0 else price_1d * 1.5
        score += min(price_7d, 15) if price_7d > 0 else price_7d * 1.0
        # Volume (20%)
        volume_ratio = volume_24h / avg_volume if avg_volume > 0 else 0
        if volume_ratio > 1.5:
            score += min((volume_ratio - 1.5) * 10, 20)
        # Volatility (20%)
        if 2 < volatility < 8:
            score += 20
        elif volatility >= 8:
            score += max(0, 20 - (volatility - 8) * 2)
        # Stability (20%)
        if symbol in ["KRW-BTC", "KRW-ETH"]:
            score += 20
        elif symbol in ["KRW-XRP", "KRW-ADA", "KRW-SOL"]:
            score += 10
        return round(score, 2)

    def select_optimal_coin(self):
        """Selects the best coin to trade based on performance and news trends."""
        print("Selecting optimal coin...")
        performance_analysis = self.get_comprehensive_coin_data()
        if not performance_analysis:
            return {'selected_coin': 'KRW-BTC', 'reason': 'Performance analysis failed.'}

        trending_coins = self.get_trending_coins_from_news()
        final_scores = self._calculate_final_scores(performance_analysis, trending_coins)

        if not final_scores:
            return {'selected_coin': 'KRW-BTC', 'reason': 'No coins to score.'}

        best_coin = max(final_scores.items(), key=lambda x: x[1]['final_score'])
        return self._format_selection_result(best_coin, performance_analysis, trending_coins, final_scores)

    def get_trending_coins_from_news(self):
        """Extracts trending coins from news headlines."""
        if not self.news_analyzer:
            return []
        # This method can be expanded from the original implementation
        return []

    def _calculate_final_scores(self, performance, trends):
        """Combines performance scores with news trends."""
        final_scores = {}
        for symbol, data in performance.items():
            base_score = data['performance_score']
            trending_bonus = 0
            for trend in trends:
                if trend['symbol'] == symbol:
                    trending_bonus = trend.get('trending_score', 0) * 0.5 # Weight news score
                    break
            final_scores[symbol] = {
                'base_score': base_score,
                'trending_bonus': trending_bonus,
                'final_score': base_score + trending_bonus,
            }
        return final_scores

    def _format_selection_result(self, best_coin, performance, trends, final_scores):
        """Formats the final result of the coin selection."""
        symbol, scores = best_coin
        return {
            'selected_coin': symbol,
            'final_score': scores['final_score'],
            'base_score': scores['base_score'],
            'trending_bonus': scores['trending_bonus'],
            'coin_data': performance.get(symbol, {}),
            'analysis_summary': {
                'total_analyzed': len(performance),
                'trending_coins_count': len(trends),
                'top_3_coins': sorted(final_scores.items(), key=lambda x: x[1]['final_score'], reverse=True)[:3]
            }
        }
    
    def print_market_summary(self, comprehensive_data):
        """Prints a summary of the market data."""
        print("Market Summary:")
        for coin, data in comprehensive_data['coins_data'].items():
            print(f"{coin}: Current Price: {data['current_price']}, "
                  f"1D Change: {data['price_change_1d']:.2f}%, "
                  f"7D Change: {data['price_change_7d']:.2f}%, "
                  f"Volume (24h): {data['volume_24h']}, "
                  f"Avg Volume: {data['avg_volume']}, "
                  f"Volatility: {data['volatility']:.2f}%, "
                  f"Performance Score: {data['performance_score']}")
