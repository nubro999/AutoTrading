# utils/logger.py
import os
import time
import json
from datetime import datetime

class TradingLogger:
    """거래 로깅 클래스"""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self._ensure_log_dir()
        
        # 로그 파일 경로
        today = datetime.now().strftime("%Y%m%d")
        self.trade_log_file = os.path.join(log_dir, f"trades_{today}.json")
        self.analysis_log_file = os.path.join(log_dir, f"analysis_{today}.json")
        self.error_log_file = os.path.join(log_dir, f"errors_{today}.log")
    
    def _ensure_log_dir(self):
        """로그 디렉토리 생성"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def log_trade(self, trade_type, amount, price, recommendation, result):
        """거래 로그 기록"""
        try:
            trade_log = {
                "timestamp": datetime.now().isoformat(),
                "trade_type": trade_type,
                "amount": amount,
                "price": price,
                "recommendation": recommendation,
                "result": result,
                "success": result is not None
            }
            
            self._append_json_log(self.trade_log_file, trade_log)
            
        except Exception as e:
            self.log_error(f"거래 로그 기록 실패: {e}")
    
    def log_analysis(self, market_data, investment_status, recommendation):
        """분석 로그 기록"""
        try:
            analysis_log = {
                "timestamp": datetime.now().isoformat(),
                "current_price": market_data.get("current_price"),
                "total_asset": investment_status.get("total_asset"),
                "recommendation": recommendation,
                "fear_greed_index": market_data.get("fear_greed_index", {}).get("current_value") if market_data.get("fear_greed_index") else None
            }
            
            self._append_json_log(self.analysis_log_file, analysis_log)
            
        except Exception as e:
            self.log_error(f"분석 로그 기록 실패: {e}")
    
    def log_error(self, error_message):
        """에러 로그 기록"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_log = f"[{timestamp}] {error_message}\n"
            
            with open(self.error_log_file, "a", encoding="utf-8") as f:
                f.write(error_log)
                
        except Exception as e:
            print(f"에러 로그 기록 실패: {e}")
    
    def _append_json_log(self, file_path, log_data):
        """JSON 로그 파일에 데이터 추가"""
        try:
            # 기존 데이터 읽기
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # 새 데이터 추가
            logs.append(log_data)
            
            # 파일에 저장
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"JSON 로그 저장 실패: {e}")
    
    def print_session_header(self):
        """세션 시작 로그 출력"""
        print("=" * 50)
        print(f"자동매매 실행 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def print_market_info(self, market_data):
        """시장 정보 출력"""
        try:
            current_price = market_data.get("current_price")
            if current_price:
                print(f"현재 BTC 가격: {current_price:,.0f}원")
            
            # 공포탐욕지수 정보
            fng_data = market_data.get("fear_greed_index")
            if fng_data:
                print(f"공포탐욕지수:")
                print(f"  - 현재값: {fng_data['current_value']} ({fng_data['current_classification']})")
                print(f"  - 7일 평균: {fng_data['average_7days']}")
                print(f"  - 트렌드: {fng_data['trend']}")
                print(f"  - 시장심리: {fng_data['market_sentiment']}")
            else:
                print("공포탐욕지수: 데이터 없음")
                
        except Exception as e:
            self.log_error(f"시장 정보 출력 오류: {e}")
    
    def print_recommendation(self, recommendation):
        """추천 정보 출력"""
        try:
            print(f"AI 추천:")
            print(f"  - 액션: {recommendation['recommendation']}")
            print(f"  - 신뢰도: {recommendation.get('confidence', 'N/A')}/10")
            print(f"  - 리스크: {recommendation.get('risk_level', 'N/A')}")
            print(f"  - 근거: {recommendation['justification']}")
            
        except Exception as e:
            self.log_error(f"추천 정보 출력 오류: {e}")
    
    def print_session_footer(self, interval=30):
        """세션 종료 로그 출력"""
        print(f"{interval}초 후 다시 실행됩니다...")
        print("=" * 50)
    
    def get_daily_summary(self):
        """일일 거래 요약"""
        try:
            if not os.path.exists(self.trade_log_file):
                return None
            
            with open(self.trade_log_file, "r", encoding="utf-8") as f:
                trades = json.load(f)
            
            if not trades:
                return None
            
            buy_trades = [t for t in trades if t["trade_type"] == "buy" and t["success"]]
            sell_trades = [t for t in trades if t["trade_type"] == "sell" and t["success"]]
            
            summary = {
                "total_trades": len(trades),
                "successful_trades": len([t for t in trades if t["success"]]),
                "buy_count": len(buy_trades),
                "sell_count": len(sell_trades),
                "total_buy_amount": sum(t["amount"] for t in buy_trades),
                "total_sell_amount": sum(t["amount"] for t in sell_trades)
            }
            
            return summary
            
        except Exception as e:
            self.log_error(f"일일 요약 생성 오류: {e}")
            return None