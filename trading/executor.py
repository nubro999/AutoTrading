# trading/executor.py
from config.settings import TradingConfig

class TradeExecutor:
    """매매 실행 클래스"""
    
    def __init__(self, upbit_client, portfolio_manager):
        self.upbit = upbit_client
        self.portfolio = portfolio_manager
        self.min_confidence = TradingConfig.MIN_CONFIDENCE
        self.trade_ratios = TradingConfig.TRADE_RATIOS
        self.min_trade_amount = TradingConfig.MIN_TRADE_AMOUNT
    
    def execute_trade(self, recommendation, investment_status):
        """매매 실행"""
        try:
            action = recommendation.get("recommendation")
            confidence = recommendation.get("confidence", 0)
            risk_level = recommendation.get("risk_level", "high")
            
            # 신뢰도 검사
            if confidence < self.min_confidence:
                print(f"신뢰도 부족으로 거래 건너뜀 (신뢰도: {confidence})")
                return False
            
            # 거래 비율 결정
            trade_ratio = self.trade_ratios.get(risk_level, self.trade_ratios["high"])
            
            # 액션별 실행
            if action == "buy":
                return self._execute_buy(investment_status, trade_ratio)
            elif action == "sell":
                return self._execute_sell(investment_status, trade_ratio)
            elif action == "hold":
                print("보유 추천")
                return True
            else:
                print(f"알 수 없는 액션: {action}")
                return False
                
        except Exception as e:
            print(f"거래 실행 오류: {e}")
            return False
    
    def _execute_buy(self, investment_status, trade_ratio):
        """매수 실행"""
        try:
            krw_balance = investment_status["krw_balance"]
            buy_amount = krw_balance * trade_ratio
            
            # 매수 가능 여부 확인
            if not self.portfolio.can_buy(buy_amount):
                print(f"매수 불가 - 잔액: {krw_balance:,.0f}원, 시도금액: {buy_amount:,.0f}원")
                return False
            
            print(f"매수 실행: {buy_amount:,.0f}원 (보유현금의 {trade_ratio*100:.0f}%)")
            
            # 실제 매수 주문
            result = self.upbit.buy_market_order(TradingConfig.TARGET_COIN, buy_amount)
            
            if result:
                print(f"매수 성공: {result}")
                return True
            else:
                print("매수 실패")
                return False
                
        except Exception as e:
            print(f"매수 실행 오류: {e}")
            return False
    
    def _execute_sell(self, investment_status, trade_ratio):
        """매도 실행"""
        try:
            btc_balance = investment_status["btc_balance"]
            btc_value = investment_status["btc_value"]
            sell_amount = btc_balance * trade_ratio
            
            # 매도 가능 여부 확인
            if not self.portfolio.can_sell(sell_amount):
                print(f"매도 불가 - BTC잔고: {btc_balance:.8f}, 평가액: {btc_value:,.0f}원")
                return False
            
            print(f"매도 실행: {sell_amount:.8f} BTC (보유BTC의 {trade_ratio*100:.0f}%)")
            
            # 실제 매도 주문
            result = self.upbit.sell_market_order(TradingConfig.TARGET_COIN, sell_amount)
            
            if result:
                print(f"매도 성공: {result}")
                return True
            else:
                print("매도 실패")
                return False
                
        except Exception as e:
            print(f"매도 실행 오류: {e}")
            return False
    
    def get_trade_size(self, investment_status, risk_level):
        """거래 크기 계산"""
        try:
            trade_ratio = self.trade_ratios.get(risk_level, self.trade_ratios["high"])
            
            krw_balance = investment_status["krw_balance"]
            btc_balance = investment_status["btc_balance"]
            
            max_buy_amount = krw_balance * trade_ratio
            max_sell_amount = btc_balance * trade_ratio
            
            return {
                "max_buy_krw": max_buy_amount,
                "max_sell_btc": max_sell_amount,
                "trade_ratio": trade_ratio
            }
            
        except Exception as e:
            print(f"거래 크기 계산 오류: {e}")
            return None
    
    def validate_trade_params(self, recommendation, investment_status):
        """거래 파라미터 유효성 검사"""
        try:
            action = recommendation.get("recommendation")
            confidence = recommendation.get("confidence", 0)
            risk_level = recommendation.get("risk_level", "high")
            
            # 기본 검사
            if action not in ["buy", "sell", "hold"]:
                return False, f"잘못된 액션: {action}"
            
            if confidence < 1 or confidence > 10:
                return False, f"잘못된 신뢰도: {confidence}"
            
            if risk_level not in ["low", "medium", "high"]:
                return False, f"잘못된 리스크 레벨: {risk_level}"
            
            # 거래 가능 여부 검사
            if action == "buy":
                trade_ratio = self.trade_ratios.get(risk_level, 0.1)
                buy_amount = investment_status["krw_balance"] * trade_ratio
                
                if not self.portfolio.can_buy(buy_amount):
                    return False, "매수 자금 부족"
            
            elif action == "sell":
                if not self.portfolio.can_sell():
                    return False, "매도할 BTC 부족"
            
            return True, "유효함"
            
        except Exception as e:
            return False, f"검사 오류: {e}"