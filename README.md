# Institutional Futures Trader

개인용 자동 선물 트레이딩 플랫폼을 기관식 운영 원칙에 가깝게 설계하는 프로젝트입니다. 초기 범위는 BingX USDT perpetual futures, 초기 심볼은 `BTC-USDT perpetual`입니다.

이 저장소의 첫 번째 목표는 빠른 매매 봇이 아니라 안전성, 테스트 가능성, 감사 가능성, 확장성을 우선하는 event-driven trading system의 기준을 문서로 고정하는 것입니다.

## Initial Scope

- Exchange: BingX
- Market: USDT perpetual futures
- Initial symbol: BTC-USDT perpetual
- Execution modes: `backtest`, `paper`, `demo`, `live`
- Default execution mode: `paper`
- Live trading: disabled by default and guarded by `docs/LIVE_TRADING_GATE.md`

## Non-Negotiable Principles

- Core trading logic must be exchange-independent.
- BingX-specific code must stay under `adapters/exchanges/bingx`.
- Strategies must not call exchange APIs directly.
- AI/ML modules must not submit orders directly.
- Every `OrderIntent` must pass through the `Risk Engine` and `OMS`.
- `Risk Engine` decisions override strategy, AI, configuration, and operator intent.
- `paper`, `demo`, and `live` should share the same core code path wherever possible.
- All important events must be auditable: `Signal`, `RiskDecision`, `Order`, `Fill`, `Position`, `PnL`, errors, and reconciliation events.

## Public Repository Safety

This repository is assumed to be public-safe.

- Never include real API keys, secrets, tokens, account IDs, wallet addresses, or exchange account details in docs, tests, logs, examples, commits, or issues.
- Never commit `.env`.
- Only `.env.example` may be committed as an environment template.
- Exchange API keys must have withdrawal permission disabled.
- Any credential-looking value in examples must be obviously non-secret and non-real.

## Live Trading Warning

Live trading must not be a simple config toggle. It requires:

- all conditions in `docs/LIVE_TRADING_GATE.md` to pass;
- explicit human approval;
- separate live-only environment variables;
- runtime confirmation that live mode was intentionally requested;
- evidence from paper/demo trading, reconciliation, and risk controls.

If live state is uncertain, the system must halt, reduce risk, or require operator review rather than continue silently.

## Current Status

This repository currently contains documentation only. Trading engine, BingX API client, strategy code, ML code, and implementation scaffold are intentionally out of scope for this first task.
