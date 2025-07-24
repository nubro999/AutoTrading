# trading/portfolio.py
import pyupbit
from config.settings import TradingConfig

class PortfolioManager:
    """포트폴리오 관리 클래스"""
    
    def __init__(self, upbit_client):
        self.upbit = upbit_client
        self.target_coin = TradingConfig.TARGET_COIN
    
    def get_investment_status(self):
        """현재 투자 상태 조회"""
        try:
            # 전체 잔고 조회
            balances = self.upbit.get_balances()
            
            # KRW 잔고
            krw_balance = self.upbit.get_balance("KRW")
            
            # BTC 잔고
            btc_balance = self.upbit.get_balance(self.target_coin) or 0
            
            # 현재 BTC 가격
            current_price = pyupbit.get_current_price(self.target_coin)
            
            # BTC 평가금액
            btc_value = btc_balance * current_price if btc_balance else 0
            
            # 총 자산 (KRW + BTC 평가금액)
            total_asset = krw_balance + btc_value
            
            # 미체결 주문 조회
            pending_orders = self.upbit.get_order(self.target_coin, state="wait")
            
            investment_status = {
                "krw_balance": krw_balance,
                "btc_balance": btc_balance,
                "btc_avg_buy_price": None,
                "btc_current_price": current_price,  
                "btc_value": btc_value,
                "total_asset": total_asset,
                "pending_orders_count": len(pending_orders) if pending_orders else 0
            }
            
            # BTC 평균 매수가 찾기
            for balance_info in balances:
                if balance_info['currency'] == 'BTC':
                    investment_status["btc_avg_buy_price"] = float(
                        balance_info.get('avg_buy_price', 0)
                    )
                    break
            
            return investment_status
            
        except Exception as e:
            print(f"투자 상태 조회 오류: {e}")
            return None
    
    def get_profit_loss(self):
        """수익률 계산"""
        try:
            status = self.get_investment_status()
            if not status:
                return None
            
            btc_balance = status["btc_balance"]
            avg_buy_price = status["btc_avg_buy_price"]
            current_price = status["btc_current_price"]
            
            if not btc_balance or not avg_buy_price:
                return {
                    "profit_loss": 0,
                    "profit_rate": 0,
                    "message": "BTC 보유 없음"
                }
            
            # 수익/손실 계산
            profit_loss = (current_price - avg_buy_price) * btc_balance
            profit_rate = ((current_price - avg_buy_price) / avg_buy_price) * 100
            
            return {
                "profit_loss": profit_loss,
                "profit_rate": profit_rate,
                "message": f"{'수익' if profit_loss > 0 else '손실'}: {abs(profit_loss):,.0f}원 ({profit_rate:+.2f}%)"
            }
            
        except Exception as e:
            print(f"수익률 계산 오류: {e}")
            return None
    
    def can_buy(self, amount):
        """매수 가능 여부 확인"""
        try:
            status = self.get_investment_status()
            if not status:
                return False
            
            return (
                status["krw_balance"] >= amount and 
                amount >= TradingConfig.MIN_TRADE_AMOUNT
            )
            
        except Exception as e:
            print(f"매수 가능 여부 확인 오류: {e}")
            return False
    
    def can_sell(self, btc_amount=None):
        """매도 가능 여부 확인"""
        try:
            status = self.get_investment_status()
            if not status:
                return False
            
            btc_balance = status["btc_balance"]
            btc_value = status["btc_value"]
            
            if btc_amount:
                # 특정 수량 매도 가능 여부
                return (
                    btc_balance >= btc_amount and 
                    btc_amount * status["btc_current_price"] >= TradingConfig.MIN_TRADE_AMOUNT
                )
            else:
                # 일반적인 매도 가능 여부
                return (
                    btc_balance > 0 and 
                    btc_value >= TradingConfig.MIN_TRADE_AMOUNT
                )
                
        except Exception as e:
            print(f"매도 가능 여부 확인 오류: {e}")
            return False
    
    def print_status(self):
        """투자 상태 출력"""
        try:
            status = self.get_investment_status()
            if not status:
                print("투자 상태 조회 실패")
                return
            
            print(f"현재 투자 상태:")
            print(f"  - KRW 잔고: {status['krw_balance']:,.0f}원")
            print(f"  - BTC 잔고: {status['btc_balance']:.8f} BTC")
            print(f"  - BTC 평가금액: {status['btc_value']:,.0f}원")
            print(f"  - 총 자산: {status['total_asset']:,.0f}원")
            
            if status['btc_avg_buy_price']:
                print(f"  - BTC 평균 매수가: {status['btc_avg_buy_price']:,.0f}원")
                
                # 수익률 정보
                pnl = self.get_profit_loss()
                if pnl:
                    print(f"  - {pnl['message']}")
            
            if status['pending_orders_count'] > 0:
                print(f"  - 미체결 주문: {status['pending_orders_count']}건")
                
        except Exception as e:
            print(f"상태 출력 오류: {e}")