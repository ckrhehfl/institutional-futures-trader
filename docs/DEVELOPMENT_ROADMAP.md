# Development Roadmap

이 문서는 PR 단위의 구현 순서와 각 단계의 non-goals를 고정합니다. 각 PR은 가능한 한 하나의 계층만 다루고, 범위 밖 제안은 follow-up PR로 남깁니다.

## 1. Domain Model v0 - completed by PR #2

목표:

- exchange-independent core domain type을 정의합니다.
- validation, invariant, public package import 경로를 테스트 가능하게 만듭니다.
- domain object가 BingX나 특정 exchange payload shape에 의존하지 않도록 고정합니다.

이번 단계에서 하지 않는 것:

- trading engine 구현
- OMS/Risk Engine 구현
- exchange adapter 구현
- REST/WebSocket 구현
- strategy/ML 구현
- paper/demo/live runtime 구현

## 2. Agent Workflow / Review Scope Guidance - this PR

목표:

- `AGENTS.md`에 Codex 작업 범위, approved minimal scaffold, hard non-goals, review guideline, PR scope rule을 명확히 적습니다.
- 앞으로 Codex review가 PR 범위 밖 구현을 요구하지 않도록 기준을 정리합니다.
- `docs/DEVELOPMENT_ROADMAP.md`에 후속 PR 순서를 고정합니다.

이번 단계에서 하지 않는 것:

- 코드 구현 또는 runtime scaffold 확장
- `pyproject.toml`, `src/trading_system`, `tests` 변경
- trading engine, OMS, Risk Engine, exchange adapter, strategy, ML, live trading 추가

## 3. Domain Events v0

목표:

- exchange-independent domain event contract를 정의합니다.
- event payload에서 secret, account identifier, raw exchange payload가 흘러들지 못하게 합니다.
- replay와 audit을 고려한 최소 event naming, timestamp, correlation convention을 정합니다.

이번 단계에서 하지 않는 것:

- event bus runtime 구현
- database/storage runtime 구현
- REST/WebSocket 연동
- exchange-specific event translation 구현
- live/demo/paper execution path 구현

## 4. Risk Engine Interface Only

목표:

- `Risk Engine`의 책임, 입력, 출력, 거부 사유, audit requirement를 interface 수준에서 정의합니다.
- `Risk Engine`이 strategy, AI, config, operator intent보다 최종 권한을 가진다는 boundary를 코드와 문서에 반영합니다.
- failure handling과 guard behavior를 테스트 우선으로 고정합니다.

이번 단계에서 하지 않는 것:

- Risk Engine policy implementation
- live capital에 영향을 주는 runtime decision path
- OMS integration
- exchange adapter integration
- strategy/ML sizing logic

## 5. OMS State Machine

목표:

- order lifecycle state와 transition rule을 exchange-independent하게 정의합니다.
- invalid transition, duplicate event, restart/replay scenario에 대한 테스트를 추가합니다.
- OMS가 exchange API를 직접 호출하지 않는 boundary를 명확히 합니다.

이번 단계에서 하지 않는 것:

- 실제 order submission
- exchange adapter 구현
- live/demo trading integration
- full trading engine runtime
- persistence runtime 확장

## 6. PaperExecutionVenue

목표:

- default execution mode인 `paper`를 simulator execution venue로 연결합니다.
- paper path가 live credential, live venue, real exchange order path에 접근하지 못함을 테스트합니다.
- core event path와 Position/PnL/Reconciliation 검증의 기반을 만듭니다.

이번 단계에서 하지 않는 것:

- live trading
- demo trading integration
- BingX REST/WebSocket client
- production deployment
- strategy 또는 ML alpha implementation

## 7. BingX Adapter Contract Tests

목표:

- BingX-specific adapter가 따라야 할 contract test를 먼저 정의합니다.
- exchange-specific 값이 core domain으로 새지 않는지 검증합니다.
- fixture policy, log redaction, raw payload handling rule을 테스트로 고정합니다.

이번 단계에서 하지 않는 것:

- 실제 REST client 구현
- 실제 WebSocket client 구현
- live/demo credential 사용
- live order submission
- production adapter deployment

## 8. Demo Trading Integration

목표:

- demo-scoped credential과 `DemoExecutionVenue`만 사용하는 통합 경로를 검증합니다.
- order lifecycle, reconciliation, failure handling, restart behavior를 demo 환경에서 확인합니다.
- paper와 demo가 같은 core event path를 공유하는지 검증합니다.

이번 단계에서 하지 않는 것:

- live trading
- withdrawal permission이 있는 key 사용
- simple config toggle로 live 전환
- 검증되지 않은 strategy/ML 자동 주문
- production deployment

## 9. Live Trading Gate, Only After Explicit Approval

목표:

- `docs/LIVE_TRADING_GATE.md` 기준을 통과한 뒤에만 live path 논의를 시작합니다.
- explicit approval, separate environment variables, runtime confirmation, non-withdrawal API key 조건을 검증합니다.
- stale, uncertain, unreconciled state에서는 halt/reduce-risk/operator-review를 우선합니다.

이번 단계에서 하지 않는 것:

- gate 승인 전 `LiveExecutionVenue` 접근
- simple config toggle 기반 live enablement
- 테스트 없는 live-trading-related code
- operator confirmation 없는 live order submission
- safety boundary를 약화하는 shortcut
