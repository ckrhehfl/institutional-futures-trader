# AGENTS.md

이 파일은 이 저장소에서 작업하는 모든 human/AI agent가 따라야 하는 project constitution입니다. 코드 구현보다 안전성, 테스트 가능성, 감사 가능성, 확장성을 우선합니다.

## Scope Rule

현재 단계에서는 문서가 source of truth입니다. 명시적 승인 없이 다음을 구현하지 마십시오.

- trading engine
- BingX API client
- strategy code
- ML/AI model code
- live trading path
- project scaffold or runtime framework

## Safety Rules

- 실제 API key, secret, token, account id, 거래소 계정 정보, wallet address를 문서나 코드에 포함하지 않습니다.
- `.env`는 절대 커밋하지 않습니다.
- `.env.example`만 커밋 가능한 environment template입니다.
- Exchange API key는 withdrawal permission이 disabled인 키만 사용한다는 전제를 문서와 코드에 반영합니다.
- Credential처럼 보이는 샘플 값은 실제 값과 혼동되지 않게 명백한 placeholder만 사용합니다.

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

## Documentation Rules

- Keep Korean prose for explanation and English names for stable domain terms and interfaces.
- Update documentation before implementing behavior that changes architecture, risk policy, order lifecycle, or live gate assumptions.
- Do not leave unfinished markers or ambiguous placeholder requirements in committed documentation.
- Define `.gitignore`, secret scanning, fixture policy, and log redaction before adding credential-loading code.
