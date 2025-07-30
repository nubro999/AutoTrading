import time
import sys
import pyupbit
from config.settings import TradingConfig
from data.market_data import MarketDataCollector
from data.coin_analyzer import CoinAnalyzer
from analysis.ai_master import AIMasterAnalyzer
from analysis.ai_analyzer import AIAnalyzer
from trading.portfolio import PortfolioManager
from trading.executor import TradeExecutor
from utils.logger import TradingLogger

class BaseTrader:
    """Base class for traders, handling common initialization and the main trading loop."""
    
    def __init__(self):
        """Initializes the trader, validates config, and sets up Upbit client and logger."""
        TradingConfig.validate()
        self.upbit = pyupbit.Upbit(
            TradingConfig.UPBIT_ACCESS_KEY, 
            TradingConfig.UPBIT_SECRET_KEY
        )
        self.logger = TradingLogger()

    def run_continuous(self): #여기서 실행!
        """Runs the trading bot in a continuous loop."""
        mode = "AI Full Auto" if isinstance(self, AIFullAutoTrader) else "Single Coin"
        print(f"Starting Auto-Trading in {mode} mode.")
        print("Press Ctrl+C to stop.")
        
        try:
            while True:
                self.run_single_cycle()
                self.logger.print_session_footer(TradingConfig.TRADE_INTERVAL)
                time.sleep(TradingConfig.TRADE_INTERVAL)
        except KeyboardInterrupt:
            self._handle_keyboard_interrupt()
        except Exception as e:
            self.logger.log_error(f"A critical error occurred in the main loop: {e}")
            print(f"A critical error occurred: {e}")

    def _handle_keyboard_interrupt(self):
        """Handles graceful shutdown on keyboard interrupt."""
        print("\nProgram shutting down.")
        summary = self.logger.get_daily_summary()
        if summary:
            print("\n=== Today's Trading Summary ===")
            print(f"Total Trades Attempted: {summary['total_trades']}")
            print(f"Successful Trades: {summary['successful_trades']}")
            print(f"Buys: {summary['buy_count']}, Sells: {summary['sell_count']}")

    def run_single_cycle(self):
        """Executes a single trading cycle. Must be implemented by subclasses."""
        raise NotImplementedError("run_single_cycle must be implemented by a subclass.")

    def run_test_mode(self):
        """Runs a single cycle in test mode without executing trades."""
        print("Running in test mode...")
        self.run_single_cycle()

class AIFullAutoTrader(BaseTrader):
    """AI-powered trader that automatically selects coins and makes all trading decisions."""

    def __init__(self):
        super().__init__()
        self.coin_analyzer = CoinAnalyzer(TradingConfig.SERPAPI_KEY)
        self.ai_master = AIMasterAnalyzer()

    def run_single_cycle(self): #이곳에서 실행!
        """Executes a single full-auto AI trading cycle."""
        try:
            self.logger.print_session_header()
            print("AI Full-Auto Mode: Analyzing market...")

            comprehensive_data = self.coin_analyzer.get_comprehensive_coin_data()
            if not comprehensive_data:
                self.logger.log_error("Failed to collect comprehensive market data.")
                return False

            self.coin_analyzer.print_market_summary(comprehensive_data)

            portfolio_manager = PortfolioManager(self.upbit)
            investment_status = self._get_comprehensive_investment_status(portfolio_manager)
            if not investment_status:
                self.logger.log_error("Failed to get comprehensive investment status.")
                self.logger.log_debug("Investment status was None or empty.")
                return False
            self._print_investment_summary(investment_status)

            print("\nAI Master is making a decision...")
            ai_decision = self._get_ai_decision(comprehensive_data, investment_status)
            if not ai_decision:
                self.logger.log_error("AI Master failed to make a decision.")
                return False
            self._print_ai_decision(ai_decision)

            success = self._execute_ai_decision(ai_decision, portfolio_manager)
            self._log_ai_cycle(comprehensive_data, investment_status, ai_decision, success)
            return success
        except Exception as e:
            self.logger.log_error(f"Error in AI full auto cycle: {e}")
            return False

    def _get_ai_decision(self, comprehensive_data, investment_status):
        """Gets a decision from the AI Master, with a fallback."""
        ai_decision = self.ai_master.analyze_and_decide(
            comprehensive_data["coins_data"],
            investment_status,
            comprehensive_data["market_context"]
        )
        if not ai_decision:
            print("AI analysis failed. Using fallback decision.")
            ai_decision = self.ai_master.get_fallback_decision(
                comprehensive_data["coins_data"],
                investment_status
            )
        return ai_decision

    def _execute_ai_decision(self, ai_decision, portfolio_manager):
        """Executes the trade recommended by the AI Master."""
        recommendation = ai_decision.get("recommendation", {})
        selected_coin = ai_decision.get("selected_coin", {}).get("symbol")

        if not selected_coin or not recommendation:
            print("Invalid AI decision structure.")
            return False

        trade_executor = TradeExecutor(self.upbit, portfolio_manager, selected_coin)
        return trade_executor.execute_trade(recommendation, portfolio_manager.get_investment_status(selected_coin))

    def _get_comprehensive_investment_status(self, portfolio_manager):
        """Gathers the investment status across all supported coins."""
        return portfolio_manager.get_comprehensive_investment_status()


    def _print_investment_summary(self, investment_status):
        """Prints a summary of the current investment portfolio."""
        # This method can be expanded from the original implementation
        print("\n" + "="*50)
        print("Current Portfolio Status")
        print("="*50)
        print(f"KRW Balance: {investment_status['krw_balance']:.0f} KRW")
        print(f"Total Coin Value: {investment_status['total_coin_value']:.0f} KRW")
        #print(f"Total Assets: {investment_status['total_asset']:.0f} KRW")


    def _print_ai_decision(self, ai_decision):
        """Prints the detailed decision from the AI Master."""
        print("\n" + "="*50)
        print("AI Master Decision")
        print("="*50)
        
        market_analysis = ai_decision.get('market_analysis', {})
        selected_coin = ai_decision.get('selected_coin', {})
        recommendation = ai_decision.get('recommendation', {})
        analysis_details = ai_decision.get('analysis_details', {})
        risk_management = ai_decision.get('risk_management', {})

        print(f"[Market Analysis]")
        print(f"- Sentiment: {market_analysis.get('overall_sentiment')}")
        print(f"- Trend: {market_analysis.get('trend_direction')}")

        print(f"\n[Selected Coin]")
        print(f"- Symbol: {selected_coin.get('symbol')}")
        print(f"- Reason: {selected_coin.get('selection_reason')}")

        print(f"\n[Recommendation]")
        print(f"- Action: {recommendation.get('action')}")
        print(f"- Confidence: {recommendation.get('confidence')}")
        print(f"- Justification: {recommendation.get('justification')}")

        print(f"\n[Analysis Details]")
        print(f"- Key Factors: {', '.join(analysis_details.get('key_factors', []))}")

        print(f"\n[Risk Management]")
        print(f"- Position Size: {risk_management.get('position_size')}")
        print(f"- Stop-Loss: {risk_management.get('stop_loss')}")
        print(f"- Take-Profit: {risk_management.get('take_profit')}")


    def _log_ai_cycle(self, comprehensive_data, investment_status, ai_decision, success):
        """Logs the entire AI cycle for later analysis."""
        # This method can be expanded from the original implementation
        self.logger.log_analysis(comprehensive_data, investment_status, ai_decision)


class SingleCoinTrader(BaseTrader):
    """A trader that focuses on a single cryptocurrency, either fixed or auto-selected."""

    def __init__(self):
        super().__init__()
        self.current_coin = None
        self.last_coin_selection_time = 0
        self.coin_analyzer = CoinAnalyzer(TradingConfig.SERPAPI_KEY) if TradingConfig.NEWS_ANALYSIS_ENABLED else None
        self.ai_analyzer = AIAnalyzer()

    def run_single_cycle(self):
        """Executes a single trading cycle for one coin."""
        try:
            self.logger.print_session_header()
            
            selected_coin = self._select_trading_coin()
            print(f"Trading coin: {selected_coin.replace('KRW-', '')}")

            market_collector = MarketDataCollector(selected_coin)
            portfolio_manager = PortfolioManager(self.upbit, selected_coin)
            trade_executor = TradeExecutor(self.upbit, portfolio_manager, selected_coin)

            investment_status = portfolio_manager.get_investment_status()
            if not investment_status:
                self.logger.log_error("Failed to get investment status.")
                return False
            portfolio_manager.print_status()

            market_data = market_collector.get_all_market_data()
            if not market_data:
                self.logger.log_error("Failed to collect market data.")
                return False
            self.logger.print_market_info(market_data)

            recommendation = self._get_ai_recommendation(market_data, investment_status, selected_coin)
            if not recommendation:
                self.logger.log_error("AI analysis failed.")
                return False
            self.logger.print_recommendation(recommendation)

            success = trade_executor.execute_trade(recommendation, investment_status)
            self.logger.log_analysis(market_data, investment_status, recommendation)
            
            return success
        except Exception as e:
            self.logger.log_error(f"Error in single coin cycle: {e}")
            return False

    def _select_trading_coin(self):
        """Selects which coin to trade based on configuration or analysis."""
        if not TradingConfig.AUTO_SELECTION_ENABLED or TradingConfig.TARGET_COIN != "AI_AUTO":
            return TradingConfig.TARGET_COIN if TradingConfig.TARGET_COIN != "AI_AUTO" else "KRW-BTC"

        # Simplified selection logic from the original file
        if self.coin_analyzer:
            selection_result = self.coin_analyzer.select_optimal_coin()
            if selection_result and 'selected_coin' in selection_result:
                self.current_coin = selection_result['selected_coin']
                return self.current_coin
        
        return self.current_coin or "KRW-BTC"

    def _get_ai_recommendation(self, market_data, investment_status, selected_coin):
        """Gets a trading recommendation from the AI analyzer."""
        coin_info = {"symbol": selected_coin, "name": selected_coin.replace('KRW-', '')}
        return self.ai_analyzer.get_recommendation(market_data, investment_status, coin_info)

def main():
    """Main function to run the trading bot."""
    
    if TradingConfig.AI_FULL_AUTO_MODE:
        trader = AIFullAutoTrader()
    else:
        trader = SingleCoinTrader()


    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        trader.run_test_mode()
    else:
        trader.run_continuous()

if __name__ == "__main__":
    main()
