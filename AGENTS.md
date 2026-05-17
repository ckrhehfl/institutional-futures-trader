# AGENTS.md

이 파일은 이 저장소에서 작업하는 모든 human/AI agent가 따라야 하는 project constitution입니다. 코드 구현보다 안전성, 테스트 가능성, 감사 가능성, 확장성을 우선합니다.

## Project Purpose

- 이 저장소는 institutional futures trading system을 만들기 위한 프로젝트입니다.
- 초기 단계에서는 실거래 구현보다 exchange-independent core domain, safety boundary, validation, tests를 우선합니다.
- 현재 단계에서는 문서와 승인된 최소 scaffold가 source of truth입니다. 명시적 승인 없이 trading runtime이나 live path를 확장하지 않습니다.

## Approved Minimal Scaffold

다음 항목은 Domain Model v0와 후속 구현을 import/test/lint 가능하게 만들기 위한 승인된 최소 scaffold입니다.

- `pyproject.toml`
- `src` layout
- `src/trading_system` package root
- `tests` directory
- pytest/ruff/pre-commit 설정
- `configs/README.md`
- `.env.example`
- `.gitignore`

이 scaffold는 runtime framework, trading engine, exchange adapter, live trading path가 아닙니다. scaffold를 이유로 event bus runtime, exchange client, strategy runtime, storage runtime, deployment path를 추가하지 않습니다.

## Scope Rule

현재 단계에서는 문서가 source of truth입니다. 명시적 승인 없이 다음을 구현하지 마십시오.

- trading engine
- BingX API client
- strategy code
- ML/AI model code
- live trading path
- project scaffold or runtime framework beyond the approved minimal scaffold

## Hard Non-Goals Unless Explicitly Requested

다음은 명시적으로 요청받기 전까지 추가하지 마십시오.

- BingX adapter
- REST client
- WebSocket client
- live trading
- trading engine
- OMS implementation
- Risk Engine implementation
- strategy implementation
- ML model
- event bus runtime
- database/storage runtime
- production deployment

## Safety Rules

- 실제 API key, secret, token, account id, 거래소 계정 정보, wallet address를 문서나 코드에 포함하지 않습니다.
- `.env`는 절대 커밋하지 않습니다.
- `.env.example`만 커밋 가능한 environment template입니다.
- Exchange API key는 withdrawal permission이 disabled인 키만 사용한다는 전제를 문서와 코드에 반영합니다.
- Credential처럼 보이는 샘플 값은 실제 값과 혼동되지 않게 명백한 placeholder만 사용합니다.
- Secret, account identifier, raw exchange payload가 `metadata`, fixture, logs, snapshots에 들어갈 수 있는 경로를 만들지 않습니다.

## Architecture Rules

- Core domain logic must be exchange-independent.
- BingX-specific code must live only under `adapters/exchanges/bingx`.
- Strategy modules may emit `Signal` only. They must not create executable orders or call exchange APIs directly.
- AI/ML modules may emit `Signal`, confidence, regime, anomaly, or sizing suggestions only. They must not create `OrderIntent` or submit orders directly.
- `Intent Builder`, `Portfolio Construction`, or `Order Intent Builder` may convert signal context into `OrderIntent`.
- All order intent must flow through `Risk Engine`, `OMS`, and `ExecutionGateway`.
- `Risk Engine` has final authority over strategy, AI, config, and operator intent.
- `paper`, `demo`, and `live` should share the same core event path.
- `paper` must route only to `PaperExecutionVenue` or simulator execution venue. `demo` must route only to `DemoExecutionVenue`. `live` must not access `LiveExecutionVenue` before `docs/LIVE_TRADING_GATE.md` passes.

## Testing Rules

Future implementation of these modules must be test-first:

- `Risk Engine`
- `OMS`
- `Order Lifecycle`
- `Position/PnL`
- `Reconciliation`

Live-trading-related code without tests is prohibited. If a change can affect live capital, it must include tests that prove failure handling and guard behavior.

Required test categories for future implementation include unit tests, invariant/property tests, replay tests, adapter contract tests, failure-injection tests, restart recovery tests, reconciliation drift tests, and negative live-guard tests.

## Live Trading Rules

- Default execution mode must be `paper`.
- `live` must not be enabled by a simple config toggle.
- `live` requires `docs/LIVE_TRADING_GATE.md` compliance, explicit approval, separate environment variables, and runtime confirmation.
- If state is uncertain, stale, or unreconciled, prefer halt/reduce-risk/operator-review over continuing.

## Review Guidelines

Codex review는 다음에 집중합니다.

- domain invariant가 깨지는지
- exchange-specific 값이 core domain으로 새는지
- secret/account/API key/raw exchange payload가 metadata로 들어갈 수 있는지
- live/demo/paper boundary가 흐려지는지
- risk boundary가 우회될 수 있는지
- regression test가 충분한지

다음은 현재 PR 범위 밖이면 follow-up으로만 언급하고 코드 변경 요구로 만들지 않습니다.

- adapter 구현
- REST/WebSocket 구현
- strategy/ML 구현
- trading engine 구현
- OMS/Risk Engine 구현
- live trading 구현
- runtime framework 확장

## PR Scope Rules

- 한 PR은 하나의 계층만 다룹니다.
- 버그성 리뷰는 같은 PR에서 처리합니다.
- 범위 밖 개선 제안은 후속 PR로 남깁니다.
- P1/P2라도 현재 PR 범위 밖이면 owner 판단을 요청하거나 follow-up으로 정리합니다.
- PR 설명에는 Scope와 Non-goals를 반드시 적습니다.

## Documentation Rules

- Keep Korean prose for explanation and English names for stable domain terms and interfaces.
- Update documentation before implementing behavior that changes architecture, risk policy, order lifecycle, or live gate assumptions.
- Do not leave unfinished markers or ambiguous placeholder requirements in committed documentation.
- Define `.gitignore`, secret scanning, fixture policy, and log redaction before adding credential-loading code.
