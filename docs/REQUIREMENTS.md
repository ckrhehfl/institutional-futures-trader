# Requirements

## Product Goal

개인용이지만 기관식 구조에 가까운 event-driven futures trading platform을 만든다. 초기 대상은 BingX USDT perpetual futures의 `BTC-USDT perpetual`이며, 빠른 기능 출시보다 safety, testability, auditability, extensibility를 우선한다.

## Execution Modes

- `backtest`: historical data로 strategy/risk/OMS behavior를 재현한다.
- `paper`: 기본 실행 모드이며 real exchange order를 제출하지 않고 `PaperExecutionVenue` 또는 simulator execution venue만 사용한다.
- `demo`: exchange-provided demo/sandbox 환경을 사용하되 core path는 paper/live와 최대한 동일해야 하며 `DemoExecutionVenue`와 demo-scoped credentials만 사용한다.
- `live`: 기본 비활성화 상태이며 `docs/LIVE_TRADING_GATE.md` 통과 전에는 `LiveExecutionVenue`에 접근할 수 없다.

## Functional Requirements

- Event-driven architecture를 사용한다.
- Core logic은 exchange-independent여야 한다.
- BingX-specific behavior는 `adapters/exchanges/bingx` 경계 안에 둔다.
- Strategy는 `Signal`만 만들 수 있으며 exchange API나 executable order path를 직접 호출할 수 없다.
- AI/ML은 `Signal`, regime detection, signal confidence, position sizing suggestion, anomaly detection, model retraining 보조 역할로 제한하며 `OrderIntent`를 만들 수 없다.
- `Intent Builder`, `Portfolio Construction`, 또는 `Order Intent Builder`만 signal context를 `OrderIntent`로 변환한다.
- 모든 order intent는 `Risk Engine`, `OMS`, `ExecutionGateway`를 통과해야 한다.
- `Risk Engine`은 모든 strategy/AI/operator 판단보다 우선한다.
- 모든 significant event를 기록한다: `Signal`, `RiskDecision`, `Order`, `Fill`, `PositionUpdate`, `PnLUpdate`, `Fee`, `FundingFee`, `ErrorEvent`, `ReconciliationEvent`.

## Futures Requirements

- Leverage 개념을 지원한다.
- Isolated/cross margin 개념을 도메인 모델과 risk policy에서 고려한다.
- `EntryPrice`, `MarkPrice`, `LiquidationRisk`, `UnrealizedPnL`, `RealizedPnL`, `FundingFee`, `Fee`, `Slippage`를 추적한다.
- `reduce_only`, `close_only`, `post_only`, `time_in_force`, one-way/hedge `PositionMode`, tick size, step size, min notional, maintenance margin, funding timestamp, ADL/deleveraging risk를 고려한다.
- Exchange actual state와 internal state를 reconciliation할 수 있어야 한다.
- Partial fill, cancelled order, rejected order, stale order state를 정상 도메인 사건으로 다룬다.

## Non-Functional Requirements

- Exchange/network latency를 제외한 internal processing latency 목표는 p95 100ms 이하이다.
- Latency must be measured by segment: event received to risk decision, risk approval to OMS command, exchange event to order state update, fill to position/PnL update.
- Audit log는 재현 가능하고 append-only 성격을 가져야 한다.
- Mode parity를 유지하여 `paper`, `demo`, `live`가 가능한 한 동일한 code path를 사용한다.
- Mode parity는 core event, risk, OMS, position, reconciliation path에 적용한다. 실제 execution venue는 `PaperExecutionVenue`, `DemoExecutionVenue`, `LiveExecutionVenue`로 명시적으로 분리한다.
- Failure state에서는 silent continuation보다 halt, risk reduction, operator review를 우선한다.

## Public Repository Requirements

- Real API key, secret, token, account id, exchange account information을 저장소에 넣지 않는다.
- `.env`는 커밋 금지이다.
- `.env.example`만 허용한다.
- API key는 withdrawal permission disabled를 원칙으로 한다.
- Future credential-loading work must add `.gitignore`, secret scanning, log redaction, and fixture policy before any real integration tests are introduced.

## Failure Handling Requirements

다음 상황은 first-class requirement이다.

- exchange REST API outage
- WebSocket disconnect/reconnect
- delayed market data or account data
- order state mismatch
- position mismatch
- partial fill and out-of-order fill events
- reconciliation drift
- restart recovery

System confidence가 낮아지면 신규 주문을 중단하고 risk state를 보수적으로 전환해야 한다.
