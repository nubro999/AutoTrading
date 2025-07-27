
# AI 완전 자동화 암호화폐 트레이딩 시스템

## 🤖 AI가 모든 것을 결정하는 완전 자동화

이제 AI가 뉴스, 공포탐욕지수, OHLCV 데이터를 종합 분석하여:
1. **어떤 코인을 거래할지 선택**
2. **매수/매도/보유 결정**
3. **투자 비중까지 결정**

모든 것을 AI가 담당합니다!

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
OPENAI_API_KEY=your_openai_api_key  # 필수!
SERPAPI_KEY=your_serpapi_key  # 선택사항 (뉴스 분석용)
```

### 4. 실행
```bash
# AI 완전 자동매매 실행
python main.py

# 테스트 모드 (분석만, 거래 없음)
python main.py --test

# 데이터 수집만 테스트
python main.py --data-test

# AI 시스템 테스트
python test_ai_full_auto.py
```

## 🧠 AI 분석 프로세스

### **1단계: 종합 시장 데이터 수집**
- **15개 주요 코인** OHLCV 데이터 (병렬 수집)
- **공포탐욕지수** 현재값 및 트렌드
- **최신 뉴스** 헤드라인 및 감성 분석
- **기술적 지표** 계산 (RSI, 이동평균, 변동성 등)

### **2단계: AI 마스터 분석**
AI가 다음을 종합 판단:
- 시장 전체 심리 및 트렌드
- 개별 코인별 기술적 분석
- 뉴스 영향도 및 시장 타이밍
- 리스크 대비 수익률

### **3단계: 최적 코인 선택**
AI가 고려하는 요소:
- 상승 잠재력 vs 하락 리스크
- 시장 모멘텀과의 일치성
- 뉴스 및 시장 심리 부합도
- 기술적 신호의 강도

### **4단계: 매매 결정 및 실행**
- **Buy**: 강한 상승 신호 + 좋은 진입 타이밍
- **Sell**: 하락 신호 + 수익 실현 타이밍
- **Hold**: 불확실성 또는 현재 포지션 유지

## 📊 실행 예시

```
🤖 AI 완전 자동매매 프로그램 시작
🧠 AI가 코인 선택부터 매매까지 모든 것을 결정합니다

🔄 AI 자동매매 사이클 #1

📊 종합 시장 데이터 수집 중...
✅ BTC 데이터 수집 완료
✅ ETH 데이터 수집 완료
✅ SOL 데이터 수집 완료
... (15개 코인)
📊 총 15개 코인 데이터 수집 완료

📊 시장 데이터 수집 결과
==================================================
😱 공포탐욕지수: 72 (Greed)
   시장심리: 탐욕 - 조심스러운 매도
📰 뉴스 감성: +0.156
   시장 신호: 상승
   분석 뉴스: 23개

🚀 1일 상승률 TOP 5:
   1. SOL: +8.34%
   2. AVAX: +6.78%
   3. MATIC: +5.23%
   4. ADA: +4.91%
   5. DOT: +3.67%

💼 현재 포트폴리오 상태
==================================================
💰 KRW 잔고: 1,000,000원
🪙 코인 평가액: 0원
📊 총 자산: 1,000,000원
📈 자산 배분: 현금 100.0%, 코인 0.0%

🧠 AI 마스터 분석 중...

🧠 AI 마스터 분석 결과
==================================================
📊 시장 전체 분석:
   전체 심리: bullish
   공포탐욕지수: 탐욕 구간이지만 뉴스 긍정적으로 상승 모멘텀 유지
   뉴스 영향: Solana DeFi 생태계 확장 소식이 시장에 긍정적 영향
   트렌드: 상승

🎯 AI 선택 코인: SOL (KRW-SOL)
   선택 이유: 최근 DeFi 생태계 확장과 기술적 상승 패턴이 결합되어 가장 높은 상승 잠재력을 보임

🟢 AI 매매 결정: BUY
   신뢰도: 8/10
   리스크: medium
   근거: 솔라나의 강한 기술적 상승 신호와 긍정적 뉴스 모멘텀이 결합되어 단기 상승 가능성이 높음. DeFi TVL 증가와 개발자 활동 증가가 펀더멘털을 뒷받침함.

🔍 세부 분석:
   기술적 신호: RSI 62로 과매수 아님, 5일선 상향 돌파
   뉴스 영향: DeFi 프로토콜 확장 소식으로 긍정적 감성
   시장 타이밍: 단기 상승 모멘텀 진입 적기
   주요 요인: 기술적 상승 패턴, DeFi 생태계 확장, 개발자 활동 증가

⚖️ 리스크 관리:
   투자 비중: 40.0%
   손절 기준: 12%
   익절 기준: 25%

💼 거래 실행: SOL BUY
💰 매수 실행: 400,000원 (보유현금의 40.0%)
✅ 매수 성공: {'uuid': 'abc123...', 'side': 'bid', 'market': 'KRW-SOL'}

✅ AI 사이클 완료
30초 후 다시 실행됩니다...
```

## 🎯 AI 결정 로직

### **시장 분석 단계**
1. **공포탐욕지수 해석**: 0-100 범위에서 시장 심리 파악
2. **뉴스 감성 종합**: 실제 헤드라인 기반 시장 영향도 분석
3. **트렌드 방향성**: 전체 시장의 흐름 판단

### **코인 선택 기준**
1. **기술적 우위**: OHLCV 패턴, RSI, 이동평균 분석
2. **뉴스 임팩트**: 해당 코인 관련 뉴스 영향도
3. **모멘텀 강도**: 단기/중기 가격 변동 패턴
4. **리스크 평가**: 변동성 대비 수익 가능성

### **매매 타이밍**
- **Buy**: 상승 신호 + 좋은 진입점 + 긍정적 뉴스
- **Sell**: 하락 위험 + 수익 실현 구간 + 부정적 신호
- **Hold**: 불확실성 높음 + 현재 포지션 적정

## ⚙️ 설정 커스터마이징

### config/settings.py
```python
# AI 완전 자동화 설정
AI_FULL_AUTO_MODE = True
MIN_CONFIDENCE = 6  # AI 신뢰도 최소 기준
TRADE_INTERVAL = 30  # 분석 주기 (초)

# 분석 대상 코인 (15개)
SUPPORTED_COINS = [
    "KRW-BTC", "KRW-ETH", "KRW-XRP", "KRW-ADA", "KRW-SOL",
    "KRW-DOGE", "KRW-AVAX", "KRW-DOT", "KRW-MATIC", "KRW-LINK",
    "KRW-UNI", "KRW-LTC", "KRW-BCH", "KRW-ATOM", "KRW-NEAR"
]

# 뉴스 분석 가중치
NEWS_WEIGHT = 0.3  # 30%
```

## 🛡️ 리스크 관리

### **AI 자체 리스크 관리**
- **최대 투자 비중**: 80% 제한
- **신뢰도 기반 거래**: 6점 이상만 실행
- **손절/익절 자동 설정**: AI가 코인별 맞춤 설정
- **포지션 사이징**: 리스크 레벨에 따른 자동 조절

### **백업 시스템**
- **AI 실패 시**: 안전한 기본 로직으로 전환
- **데이터 부족 시**: 보수적 접근으로 리스크 최소화
- **API 오류 시**: 거래 중단 및 에러 로깅

## 💡 주요 장점

1. **완전 자동화**: 인간 개입 없이 24/7 운영
2. **지능형 판단**: 15개 코인 중 최적 선택
3. **종합 분석**: 기술적 + 뉴스 + 심리 통합 분석
4. **적응형 리스크**: 시장 상황에 맞는 동적 리스크 관리
5. **실시간 반응**: 시장 변화에 즉각 대응

## 🚨 주의사항

1. **OpenAI API 필수**: GPT-4 분석을 위해 반드시 필요
2. **충분한 자금**: 다양한 코인 거래를 위한 적정 자금 권장
3. **시장 변동성**: 높은 변동성 시기에는 더 보수적 접근
4. **정기 모니터링**: 완전 자동화이지만 주기적 점검 권장

## 🔄 업그레이드 포인트

- **더 많은 코인**: 지원 코인 확대 (알트코인 포함)
- **고급 지표**: MACD, 볼린저 밴드 등 추가
- **감정 분석**: 소셜 미디어 감성 분석 추가
- **백테스팅**: 과거 데이터로 전략 검증

이제 AI가 모든 것을 담당하는 완전 자동화 트레이딩 시스템이 완성되었습니다! 🤖✨## 📊 실행 예시
```
🔍 최적 코인 선택 분석 중...
🏆 선택된 코인: SOL (KRW-SOL)
📊 최종 점수: 87.30점
  - 기본 성과: 72.50점  
  - 뉴스 보너스: 14.80점

현재 투자 상태 (KRW-SOL):
  - KRW 잔고: 1,000,000원
  - SOL 잔고: 0.00000000 SOL
  - 총 자산: 1,000,000원

🔍 뉴스 분석 중...
현재 SOL 가격: 185,400원
뉴스 감성 분석:
  - 전체 감성: +0.234
  - 시장 신호: 상승
  - 분석 뉴스: 18개
  - 긍정: 12개, 부정: 3개

AI 추천:
  - 액션: buy
  - 신뢰도: 8/10
  - 뉴스 영향도: high
  - 주요 요인: ["뉴스 긍정적 감성", "가격 상승 모멘텀", "거래량 증가"]
```# 비트코인 자동매매 프로그램 사용법

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
SERPAPI_KEY=your_serpapi_key  # 뉴스 분석용 (선택사항)
```

### 4. 실행
```bash
# 일반 실행 (자동매매 + 자동 코인 선택)
python main.py

# 테스트 모드 (분석만, 거래 없음)
python main.py --test

# 코인 선택 테스트
python main.py --coin-select

# 뉴스 분석 테스트
python test_news_analysis.py

# 코인 선택 테스트
python test_coin_selection.py
```

## 📁 모듈별 기능

### config/settings.py
- 모든 설정값 중앙 관리
- API 키, 거래 설정, 코인 선택 설정 등

### data/coin_selector.py
- **자동 코인 선택**: 15개 주요 코인 중 최적 선택
- **성과 분석**: 가격 모멘텀, 거래량, 변동성 등 종합 분석
- **뉴스 트렌딩**: 뉴스 언급도와 감성 분석 기반 트렌딩 코인 선정
- **종합 점수**: 기술적 분석 + 뉴스 감성을 조합한 최종 점수

### data/news_analyzer.py
- SerpAPI를 통한 Google News 데이터 수집  
- 비트코인/암호화폐 관련 뉴스 감성 분석
- 키워드 기반 감성 점수 계산
- 시간 가중치 적용한 종합 분석

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

### 자동 코인 선택 설정
`config/settings.py`에서 설정 변경:
```python
TARGET_COIN = "AUTO"  # 자동 선택 활성화
AUTO_SELECTION_ENABLED = True
COIN_ANALYSIS_INTERVAL = 3600  # 1시간마다 재분석
SUPPORTED_COINS = ["KRW-BTC", "KRW-ETH", ...]  # 분석 대상 코인
```

### 특정 코인 고정
```python
TARGET_COIN = "KRW-ETH"  # 이더리움 고정
AUTO_SELECTION_ENABLED = False
```

### SerpAPI 뉴스 분석 설정
1. [SerpAPI](https://serpapi.com/)에서 API 키 발급
2. `.env` 파일에 `SERPAPI_KEY` 추가
3. `config/settings.py`에서 뉴스 가중치 조정:
   - `NEWS_WEIGHT`: 뉴스 감성의 거래 결정 영향도 (0.0 ~ 1.0)

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