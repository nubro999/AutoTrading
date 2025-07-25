# trading/portfolio.py
import pyupbit
from config.settings import TradingConfig

class PortfolioManager:
    """포트폴리오 관리 클래스"""
    
    def __init__(self, upbit_client, target_coin=None):
        self.upbit = upbit_client
        self.target_coin = target_coin or TradingConfig.TARGET_COIN
    
    def get_investment_status(self, coin_symbol=None):
        """현재 투자 상태 조회"""
        try:
            target_coin = coin_symbol or self.target_coin
            coin_currency = target_coin.replace('KRW-', '')
            
            # 전체 잔고 조회
            balances = self.upbit.get_balances()
            
            # KRW 잔고
            krw_balance = self.upbit.get_balance("KRW")
            
            # 코인 잔고
            coin_balance = self.upbit.get_balance(target_coin) or 0
            
            # 현재 코인 가격
            current_price = pyupbit.get_current_price(target_coin)
            
            # 코인 평가금액
            coin_value = coin_balance * current_price if coin_balance else 0
            
            # 총 자산 (KRW + 코인 평가금액)
            total_asset = krw_balance + coin_value
            
            # 미체결 주문 조회
            pending_orders = self.upbit.get_order(target_coin, state="wait")
            
            investment_status = {
                "target_coin": target_coin,
                "coin_currency": coin_currency,
                "krw_balance": krw_balance,
                "coin_balance": coin_balance,
                "coin_avg_buy_price": None,
                "coin_current_price": current_price,  
                "coin_value": coin_value,
                "total_asset": total_asset,
                "pending_orders_count": len(pending_orders) if pending_orders else 0
            }
            
            # 코인 평균 매수가 찾기
            for balance_info in balances:
                if balance_info['currency'] == coin_currency:
                    investment_status["coin_avg_buy_price"] = float(
                        balance_info.get('avg_buy_price', 0)
                    )
                    break
            
            return investment_status
            
        except Exception as e:
            print(f"투자 상태 조회 오류: {e}")
            return None
    
    def get_profit_loss(self, coin_symbol=None):
        """수익률 계산"""
        try:
            status = self.get_investment_status(coin_symbol)
            if not status:
                return None
            
            coin_balance = status["coin_balance"]
            avg_buy_price = status["coin_avg_buy_price"]
            current_price = status["coin_current_price"]
            coin_name = status["coin_currency"]
            
            if not coin_balance or not avg_buy_price:
                return {
                    "profit_loss": 0,
                    "profit_rate": 0,
                    "message": f"{coin_name} 보유 없음"
                }
            
            # 수익/손실 계산
            profit_loss = (current_price - avg_buy_price) * coin_balance
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
    
    def can_sell(self, coin_amount=None, coin_symbol=None):
        """매도 가능 여부 확인"""
        try:
            status = self.get_investment_status(coin_symbol)
            if not status:
                return False
            
            coin_balance = status["coin_balance"]
            coin_value = status["coin_value"]
            
            if coin_amount:
                # 특정 수량 매도 가능 여부
                return (
                    coin_balance >= coin_amount and 
                    coin_amount * status["coin_current_price"] >= TradingConfig.MIN_TRADE_AMOUNT
                )
            else:
                # 일반적인 매도 가능 여부
                return (
                    coin_balance > 0 and 
                    coin_value >= TradingConfig.MIN_TRADE_AMOUNT
                )
                
        except Exception as e:
            print(f"매도 가능 여부 확인 오류: {e}")
            return False
    
    def print_status(self, coin_symbol=None):
        """투자 상태 출력"""
        try:
            status = self.get_investment_status(coin_symbol)
            if not status:
                print("투자 상태 조회 실패")
                return
            
            coin_name = status["coin_currency"]
            
            print(f"현재 투자 상태 ({status['target_coin']}):")
            print(f"  - KRW 잔고: {status['krw_balance']:,.0f}원")
            print(f"  - {coin_name} 잔고: {status['coin_balance']:.8f} {coin_name}")
            print(f"  - {coin_name} 평가금액: {status['coin_value']:,.0f}원")
            print(f"  - 총 자산: {status['total_asset']:,.0f}원")
            
            if status['coin_avg_buy_price']:
                print(f"  - {coin_name} 평균 매수가: {status['coin_avg_buy_price']:,.0f}원")
                
                # 수익률 정보
                pnl = self.get_profit_loss(coin_symbol)
                if pnl:
                    print(f"  - {pnl['message']}")
            
            if status['pending_orders_count'] > 0:
                print(f"  - 미체결 주문: {status['pending_orders_count']}건")
                
        except Exception as e:
            print(f"상태 출력 오류: {e}")