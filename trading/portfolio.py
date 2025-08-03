# trading/portfolio.py
import pyupbit
from config.settings import TradingConfig
from utils.logger import TradingLogger
import traceback

class PortfolioManager:

    """포트폴리오 관리 클래스"""
    
    def __init__(self, upbit_client, target_coin=None):
        self.upbit = upbit_client
        self.target_coin = target_coin or TradingConfig.TARGET_COIN
        self.logger = TradingLogger()
    
    def get_investment_status(self, coin_symbol=None):
        """현재 투자 상태 조회"""
        try:
            target_coin = coin_symbol or self.target_coin
            coin_currency = target_coin.replace('KRW-', '')
            
            # 전체 잔고 조회 및 요약 출력
            balances = self.upbit.get_balances()
            self._log_balances_summary(balances, target_coin)
            
            # KRW 잔고
            krw_balance = self.upbit.get_balance("KRW")
            
            # 코인 잔고
            try:
                coin_balance = self.upbit.get_balance(coin_currency) or 0
            except Exception as balance_error:
                print(f"[WARNING] Balance error for {coin_currency}: {balance_error}")
                coin_balance = 0
            
            # 현재 코인 가격
            try:
                current_price = pyupbit.get_current_price(target_coin)
                if current_price is None:
                    current_price = 0
            except Exception as price_error:
                print(f"[WARNING] Price error for {target_coin}: {price_error}")
                current_price = 0
            
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
            print(f"[ERROR] Investment status error: {e}")
            return None
    
    def _log_balances_summary(self, balances, target_coin):
        """잔고 요약을 컴팩트하게 출력"""
        try:
            print(f"[INFO] Balance check for {target_coin}:")
            
            # 보유 중인 코인들만 표시
            held_coins = []
            krw_balance = 0
            
            for balance in balances:
                currency = balance['currency']
                amount = float(balance['balance'])
                
                if currency == 'KRW':
                    krw_balance = amount
                elif amount > 0:
                    held_coins.append(f"{currency}: {amount:.8f}")
            
            print(f"   KRW: {krw_balance:,.0f}")
            if held_coins:
                print(f"   Coins: {', '.join(held_coins[:5])}")  # Show max 5 coins
                if len(held_coins) > 5:
                    print(f"   ... and {len(held_coins) - 5} more")
            else:
                print("   No coins held")
                
        except Exception as e:
            print(f"[WARNING] Error showing balance summary: {e}")

    def get_comprehensive_investment_status(self):
        """모든 지원되는 코인에 대한 종합적인 투자 상태를 조회합니다."""
        try:
            balances = self.upbit.get_balances()
            self.logger.log_debug(f"Fetched balances: {balances}")
            krw_balance = 0
            total_coin_value = 0
            all_coins_status = []

            # Find KRW balance first
            for balance in balances:
                if balance['currency'] == 'KRW':
                    krw_balance = float(balance['balance'])
                    break
            self.logger.log_debug(f"KRW Balance: {krw_balance}")

            for coin_symbol in TradingConfig.SUPPORTED_COINS:
                coin_currency = coin_symbol.replace('KRW-', '')
                coin_balance = 0
                avg_buy_price = 0
                
                for balance in balances:
                    if balance['currency'] == coin_currency:
                        coin_balance = float(balance['balance'])
                        avg_buy_price = float(balance.get('avg_buy_price', 0))
                        break
                self.logger.log_debug(f"Processing {coin_symbol}: Balance={coin_balance}, Avg Buy Price={avg_buy_price}")

                if coin_balance > 0:
                    import time
                    current_price = None
                    
                    # Try to get price with retry logic
                    for attempt in range(4):  # 0, 1, 2, 3 (4 attempts total)
                        try:
                            current_price = pyupbit.get_current_price(coin_symbol)
                            self.logger.log_debug(f"Current price for {coin_symbol} (attempt {attempt + 1}): {current_price}")
                            
                            # If we got a valid price, break out of retry loop
                            if current_price is not None and current_price > 0:
                                break
                                
                            # If price is invalid and we have more attempts, retry after delay
                            if attempt < 3:
                                delay = (attempt + 1) * 0.5  # 0.5s, 1s, 1.5s delays
                                self.logger.log_debug(f"Invalid price ({current_price}), retrying {coin_symbol} after {delay}s delay...")
                                time.sleep(delay)
                            
                        except Exception as e:
                            self.logger.log_warning(f"Failed to get current price for {coin_symbol} (attempt {attempt + 1}): {e}")
                            if attempt < 3:
                                time.sleep((attempt + 1) * 0.5)

                    if current_price is None or current_price == 0:
                        self.logger.log_warning(f"Current price for {coin_symbol} is invalid ({current_price}) after all retries. Skipping this coin.")
                        continue
                    
                    coin_value = coin_balance * current_price
                    total_coin_value += coin_value
                    all_coins_status.append({
                        "symbol": coin_symbol,
                        "balance": coin_balance,
                        "avg_buy_price": avg_buy_price,
                        "current_price": current_price,
                        "value": coin_value
                    })
                else:
                    self.logger.log_debug(f"No balance for {coin_symbol}. Skipping.")

            total_asset = krw_balance + total_coin_value
            
            return {
                "krw_balance": krw_balance,
                "total_coin_value": total_coin_value,
                #"total_asset": total_asset,
                "held_coins": all_coins_status
            }

        except Exception as e:
            self.logger.log_error(f"종합 투자 상태 조회 오류: {e}\n{traceback.format_exc()}")
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