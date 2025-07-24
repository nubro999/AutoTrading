# main.py
import time
import pyupbit
from config.settings import TradingConfig
from data.market_data import MarketDataCollector
from trading.portfolio import PortfolioManager
from trading.executor import TradeExecutor
from analysis.ai_analyzer import AIAnalyzer
from utils.logger import TradingLogger

class BitcoinAutoTrader:
    """비트코인 자동매매 메인 클래스"""
    
    def __init__(self):
        # 설정 검증
        TradingConfig.validate()
        
        # 업비트 클라이언트 초기화
        self.upbit = pyupbit.Upbit(
            TradingConfig.UPBIT_ACCESS_KEY, 
            TradingConfig.UPBIT_SECRET_KEY
        )
        
        # 컴포넌트 초기화
        self.market_collector = MarketDataCollector()
        self.portfolio_manager = PortfolioManager(self.upbit)
        self.trade_executor = TradeExecutor(self.upbit, self.portfolio_manager)
        self.ai_analyzer = AIAnalyzer()
        self.logger = TradingLogger()
    
    def run_single_cycle(self):
        """단일 거래 사이클 실행"""
        try:
            # 세션 시작 로그
            self.logger.print_session_header()
            
            # 1. 현재 투자 상태 조회
            investment_status = self.portfolio_manager.get_investment_status()
            if not investment_status:
                self.logger.log_error("투자 상태 조회 실패")
                return False
            
            # 포트폴리오 상태 출력
            self.portfolio_manager.print_status()
            
            # 2. 시장 데이터 수집
            market_data = self.market_collector.get_all_market_data()
            if not market_data:
                self.logger.log_error("시장 데이터 수집 실패")
                return False
            
            # 시장 정보 출력
            self.logger.print_market_info(market_data)
            
            # 3. AI 분석 및 추천
            recommendation = self.ai_analyzer.get_recommendation(
                market_data, investment_status
            )
            if not recommendation:
                self.logger.log_error("분석 실패")
                return False
            
            # 추천 정보 출력
            self.logger.print_recommendation(recommendation)
            
            # 4. 거래 실행
            success = self.trade_executor.execute_trade(
                recommendation, investment_status
            )
            
            # 5. 로그 기록
            self.logger.log_analysis(market_data, investment_status, recommendation)
            
            if success and recommendation["recommendation"] in ["buy", "sell"]:
                trade_size = self.trade_executor.get_trade_size(
                    investment_status, recommendation["risk_level"]
                )
                
                self.logger.log_trade(
                    recommendation["recommendation"],
                    trade_size["max_buy_krw"] if recommendation["recommendation"] == "buy" else trade_size["max_sell_btc"],
                    market_data["current_price"],
                    recommendation,
                    "success" if success else "failed"
                )
            
            return True
            
        except Exception as e:
            self.logger.log_error(f"거래 사이클 실행 오류: {e}")
            return False
    
    def run_continuous(self):
        """연속 자동매매 실행"""
        print("비트코인 자동매매 프로그램 시작")
        print("종료하려면 Ctrl+C를 누르세요.")
        
        try:
            while True:
                # 단일 사이클 실행
                self.run_single_cycle()
                
                # 대기
                self.logger.print_session_footer(TradingConfig.TRADE_INTERVAL)
                time.sleep(TradingConfig.TRADE_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n프로그램을 종료합니다.")
            
            # 일일 요약 출력
            summary = self.logger.get_daily_summary()
            if summary:
                print("\n=== 오늘의 거래 요약 ===")
                print(f"총 거래 시도: {summary['total_trades']}회")
                print(f"성공한 거래: {summary['successful_trades']}회")
                print(f"매수: {summary['buy_count']}회")
                print(f"매도: {summary['sell_count']}회")
                
        except Exception as e:
            self.logger.log_error(f"프로그램 오류: {e}")
            print(f"프로그램 오류: {e}")
    
    def run_test_mode(self):
        """테스트 모드 실행 (실제 거래 없이 분석만)"""
        print("=== 테스트 모드 ===")
        
        try:
            # 시장 데이터 수집
            market_data = self.market_collector.get_all_market_data()
            if not market_data:
                print("시장 데이터 수집 실패")
                return
            
            # 투자 상태 조회
            investment_status = self.portfolio_manager.get_investment_status()
            if not investment_status:
                print("투자 상태 조회 실패")
                return
            
            # 상태 출력
            self.portfolio_manager.print_status()
            self.logger.print_market_info(market_data)
            
            # AI 분석
            recommendation = self.ai_analyzer.get_recommendation(
                market_data, investment_status
            )
            
            if recommendation:
                self.logger.print_recommendation(recommendation)
                
                # 거래 파라미터 검증
                is_valid, message = self.trade_executor.validate_trade_params(
                    recommendation, investment_status
                )
                print(f"거래 가능 여부: {message}")
                
                if is_valid:
                    trade_size = self.trade_executor.get_trade_size(
                        investment_status, recommendation["risk_level"]
                    )
                    print(f"예상 거래 크기: {trade_size}")
            else:
                print("분석 실패")
                
        except Exception as e:
            print(f"테스트 모드 오류: {e}")

def main():
    """메인 함수"""
    import sys
    
    trader = BitcoinAutoTrader()
    
    # 명령행 인자에 따른 실행 모드 결정
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        trader.run_test_mode()
    else:
        trader.run_continuous()

if __name__ == "__main__":
    main()