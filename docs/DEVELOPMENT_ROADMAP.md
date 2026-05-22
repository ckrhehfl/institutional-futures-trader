# Development Roadmap

이 문서는 PR 단위의 구현 순서와 각 단계의 non-goals를 고정합니다. 각 PR은 가능한 한 하나의 계층만 다루고, 범위 밖 제안은 follow-up PR로 남깁니다.

## 1. Domain Model v0 / Approved Minimal Scaffold

목표:

- approved minimal scaffold를 별도 선행 PR에서 추가합니다: `pyproject.toml`, `src` layout, `src/trading_system` package root, `tests` directory, pytest/ruff/pre-commit 설정, `configs/README.md`, `.env.example`, `.gitignore`.
- exchange-independent core domain model을 정의합니다.
- validation, invariant, public package import 경로를 테스트 가능하게 만듭니다.
- core domain model, validation, tests가 후속 PR에서 import/test/lint 가능한 기준선이 되도록 정리합니다.
- domain object가 BingX나 특정 exchange payload shape에 의존하지 않도록 고정합니다.
- 해당 선행 PR이 merge되기 전에는 scaffold, package root, tests가 main에 존재한다고 가정하지 않습니다.

이번 단계에서 하지 않는 것:

- approved minimal scaffold를 runtime framework로 취급하지 않습니다.
- trading engine 구현
- OMS/Risk Engine 구현
- exchange adapter 구현
- REST/WebSocket 구현
- strategy/ML 구현
- paper/demo/live runtime 구현

## 2. Agent Workflow / Review Scope Guidance - PR #3

목표:

- 이번 PR #3은 문서와 repository-level agent guidance만 정리합니다.
- `AGENTS.md`에 Codex 작업 범위, approved minimal scaffold, hard non-goals, review guideline, PR scope rule을 명확히 적습니다.
- 앞으로 Codex review가 PR 범위 밖 구현을 요구하지 않도록 기준을 정리합니다.
- `docs/DEVELOPMENT_ROADMAP.md`에 후속 PR 순서를 고정합니다.

이번 단계에서 하지 않는 것:

- 이번 PR에서 새 Python code나 새 scaffold를 추가하지 않습니다.
- 이번 PR에서 `pyproject.toml`, `src/trading_system`, `tests`를 수정하지 않습니다.
- 선행 scaffold/domain PR의 필요성을 부정하거나 건너뛰지 않습니다.
- trading engine, OMS, Risk Engine, exchange adapter, strategy, ML, live trading 추가

## 3. PR Review Loop Lessons / Compound Learning Guardrails - PR #5

목표:

- PR #2, PR #3, PR #4의 review loop와 scope 판단 교훈을 `docs/solutions/`에 기록합니다.
- 리뷰 코멘트 분류와 처리 기준을 `docs/PR_REVIEW_PLAYBOOK.md`에 정리합니다.
- PR template에 Scope, Non-goals, Allowed files / layers, Validation, Compound learning note를 추가합니다.
- AGENTS.md에 review triage와 compound learning loop를 짧게 반영합니다.

이번 단계에서 하지 않는 것:

- Python code 변경
- `pyproject.toml`, `src/trading_system`, `tests` 변경
- trading engine, OMS, Risk Engine, exchange adapter, REST/WebSocket, strategy, ML, live trading 구현
- custom skill 생성

## 4. Domain Events v0 - next implementation step

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

## 5. Risk Engine Interface Only - completed

목표:

- `Risk Engine`의 책임, 입력, 출력, 거부 사유, audit requirement를 interface 수준에서 정의합니다.
- `Risk Engine`이 strategy, AI, config, operator intent보다 최종 권한을 가진다는 boundary를 코드와 문서에 반영합니다.
- failure handling과 guard behavior를 테스트 우선으로 고정합니다.
- 이 단계는 Risk Engine interface contract만 고정한 previous implementation step입니다.

이번 단계에서 하지 않는 것:

- Risk Engine policy implementation
- live capital에 영향을 주는 runtime decision path
- OMS integration
- exchange adapter integration
- strategy/ML sizing logic

## 6. OMS State Machine - current implementation step

목표:

- order lifecycle state와 transition rule을 exchange-independent하게 정의합니다.
- PR #50에서는 Step 6 전체가 아니라 exchange-independent OMS State Machine v0 pure helper만 구현합니다.
- `OrderStatus` transition policy와 validation helper를 추가합니다.
- invalid transition은 fail closed로 거부합니다.
- terminal / no-auto-forward states를 명확히 고정합니다.
- positive / negative transition tests로 state machine boundary를 검증합니다.
- OMS가 exchange API를 직접 호출하지 않는 boundary를 유지합니다.

이번 단계에서 하지 않는 것:

- OMS runtime 구현
- 실제 order submission
- exchange adapter 구현
- ExecutionGateway 구현
- Risk Engine implementation
- event bus/storage runtime 구현
- reconciliation runtime 구현
- live/demo trading integration
- full trading engine runtime
- live trading path
- persistence runtime 확장

## 7. Backtest / Historical Replay

목표:

- `backtest` execution mode와 deterministic historical replay 요구사항을 paper execution 전에 명확히 검증합니다.
- replayed fees, slippage assumptions, funding treatment, PnL, drawdown, risk decision history를 검증 가능한 산출물로 남깁니다.
- paper/demo/live와 같은 core domain boundary를 사용하되 real exchange order path에 접근하지 않도록 합니다.

이번 단계에서 하지 않는 것:

- live trading
- demo trading integration
- BingX REST/WebSocket client
- production deployment
- live capital에 영향을 주는 runtime decision path

## 8. PaperExecutionVenue

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

## 9. BingX Adapter Contract Tests

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

## 10. Demo Trading Integration

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

## 11. Live Trading Gate, Only After Explicit Approval

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
