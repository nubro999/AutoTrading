# 비트코인 자동매매 프로그램 사용법

## 🚀 설치 및 실행

### 1. 프로젝트 구조 생성
```bash
mkdir bitcoin_trading
cd bitcoin_trading

# 각 디렉토리 생성
mkdir config data analysis trading utils logs
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정 (.env 파일)
```env
UPBIT_ACCESS_KEY=your_upbit_access_key
UPBIT_SECRET_KEY=your_upbit_secret_key  
OPENAI_API_KEY=your_openai_api_key  # 선택사항
```

### 4. 실행
```bash
# 일반 실행 (실제 거래)
python main.py

# 테스트 모드 (분석만, 거래 없음)
python main.py --test
```

## 📁 모듈별 기능

### config/settings.py
- 모든 설정값 중앙 관리
- API 키, 거래 설정, 임계값 등

### data/market_data.py
- 업비트 시장 데이터 수집
- OHLCV, 현재가, 호가 정보

### data/fear_greed.py  
- 공포탐욕지수 API 연동
- 트렌드 분석 및 거래 팩터 계산

### analysis/ai_analyzer.py
- OpenAI GPT-4를 이용한 AI 분석
- 프롬프트 관리 및 응답 검증

### analysis/technical_analyzer.py
- 기술적 분석 (백업용)
- 이동평균, RSI 등 계산

### trading/portfolio.py
- 포트폴리오 상태 관리
- 잔고, 수익률 계산

### trading/executor.py
- 실제 매매 실행
- 리스크 관리 및 거래량 조절

### utils/logger.py
- 거래 로그 기록
- 일일/에러 로그 관리

## 🔧 커스터마이징

### 거래 설정 변경
`config/settings.py`에서 다음 값들을 조정:
- `MIN_CONFIDENCE`: 최소 신뢰도 (기본: 6)
- `TRADE_RATIOS`: 리스크별 거래 비율
- `TRADE_INTERVAL`: 거래 주기 (기본: 30초)

### AI 프롬프트 수정
`analysis/ai_analyzer.py`의 `_get_system_prompt()` 메서드에서 프롬프트 수정 가능

### 로그 확인
- `logs/trades_YYYYMMDD.json`: 거래 기록
- `logs/analysis_YYYYMMDD.json`: 분석 기록  
- `logs/errors_YYYYMMDD.log`: 에러 로그

## ⚠️ 주의사항

1. **테스트 모드로 먼저 실행**하여 정상 작동 확인
2. **소액으로 시작**하여 전략 검증
3. **로그를 정기적으로 확인**하여 성과 모니터링
4. **API 키는 절대 공유하지 말 것**

## 🛠️ 문제 해결

### API 오류
- 업비트 API 키 권한 확인
- IP 화이트리스트 설정 확인

### OpenAI 오류  
- API 키 유효성 확인
- 크레딧 잔액 확인
- AI 없이도 백업 분석으로 작동 가능

### 거래 실패
- 최소 거래 금액 확인 (5,000원)
- 잔고 부족 여부 확인
- 네트워크 연결 상태 확인

## 📊 성과 모니터링

### 일일 요약 확인
프로그램 종료 시 자동으로 출력되는 일일 거래 요약:
- 총 거래 시도 횟수
- 성공한 거래 횟수  
- 매수/매도 횟수
- 거래 금액

### 로그 분석
```python
# 거래 로그 분석 예시
import json
with open('logs/trades_20241124.json', 'r') as f:
    trades = json.load(f)

# 성공률 계산
success_rate = len([t for t in trades if t['success']]) / len(trades) * 100
print(f"거래 성공률: {success_rate:.1f}%")
```

## 🔄 확장 가능성

### 새로운 지표 추가
`analysis/technical_analyzer.py`에 새로운 기술적 지표 메서드 추가:
```python
def calculate_macd(self, df, fast=12, slow=26, signal=9):
    # MACD 계산 로직
    pass
```

### 다른 코인 지원  
`config/settings.py`에서 `TARGET_COIN` 변경:
```python
TARGET_COIN = "KRW-ETH"  # 이더리움
```

### 알림 기능 추가
`utils/logger.py`에 텔레그램/슬랙 알림 기능 추가 가능

### 백테스팅 모듈
과거 데이터로 전략 검증하는 모듈 추가 가능

## 🚨 리스크 관리

### 손절매 설정
`trading/executor.py`에 손절매 로직 추가:
```python
def check_stop_loss(self, investment_status, stop_loss_rate=0.05):
    # 5% 손실 시 자동 매도
    pass
```

### 최대 투자 한도
설정에서 최대 투자 비율 제한:
```python
MAX_INVESTMENT_RATIO = 0.8  # 총 자산의 80%까지만
```

## 💡 최적화 팁

1. **거래 주기 조정**: 너무 자주 거래하면 수수료 부담
2. **신뢰도 임계값**: 높일수록 안전하지만 기회 감소
3. **공포탐욕지수 활용**: 극단적 상황에서 더 공격적 거래
4. **리스크 레벨**: 시장 상황에 따라 동적 조정 고려

이제 모든 모듈이 완성되었습니다! 기존의 600줄 코드가 8개의 깔끔한 모듈로 분리되어 훨씬 관리하기 쉬워졌어요. 각 모듈이 명확한 역할을 가지고 있어서 수정이나 확장도 간편합니다.