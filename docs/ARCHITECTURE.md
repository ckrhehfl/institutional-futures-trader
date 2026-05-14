# Architecture

## Architectural Intent

이 시스템은 단순 trading bot이 아니라 event-driven trading system이다. Core는 exchange-independent이고, exchange adapter만 외부 거래소와 통신한다.

## High-Level Flow

```text
Market Data / Account Data
        |
        v
Event Bus -> Strategy / AI Assistants
        |          |
        |          v
        |      Signal / Advisory Suggestion
        |          |
        v          v
Intent Builder / Portfolio Construction -> OrderIntent
        |
        v
Risk Engine -> RiskDecision
        |
        v
OMS -> Order Command
        |
        v
Execution Gateway -> Execution Venue
        |
        v
Exchange Adapter -> BingX
        |
        v
Fill / Account Event / Reconciliation Event
```

## Core Boundaries

Core modules must not depend on BingX-specific API shapes.

- `Strategy`: consumes market/domain events and emits `Signal` only.
- `AI/ML`: emits advisory metadata only, such as confidence, regime, anomaly, or sizing suggestion.
- `Intent Builder/Portfolio Construction`: converts signal context into `OrderIntent` without bypassing risk.
- `Risk Engine`: validates or rejects every `OrderIntent`.
- `OMS`: owns order state transitions after risk approval.
- `Execution Gateway`: selects simulator, demo, or live execution venue after all mode guards pass.
- `Portfolio/Position`: tracks exposure, margin, PnL, fees, and funding.
- `Reconciliation`: compares internal state with exchange actual state.
- `Exchange Adapter`: translates core commands/events to exchange-specific APIs.

## Exchange Boundary

BingX-specific code must live only under:

```text
adapters/exchanges/bingx
```

Core must communicate with adapters through stable exchange-neutral contracts. Strategy, AI, Risk Engine, OMS, and Portfolio modules must not import BingX client code.

Core event and type names must not mirror BingX response fields. Symbol mapping, order status mapping, error-code mapping, and authentication behavior belong inside the BingX adapter boundary.

## Mode Parity

`paper`, `demo`, and `live` should share the same event, risk, OMS, position, and reconciliation path. Differences should be isolated at execution/account data boundaries.

The default mode is always `paper`. `live` requires the live gate and cannot be enabled by a single config value.

Execution venue rules:

- `paper` routes only to a simulator venue and must never instantiate a live exchange order path.
- `demo` routes only to a demo/sandbox venue with demo-scoped credentials.
- `live` routes only through `LiveTradingGuard` after `docs/LIVE_TRADING_GATE.md` passes.
- Venue selection must fail closed when mode, credentials, or approval state are ambiguous.

## Auditability

Every material decision and state transition must be recorded with:

- timestamp
- mode
- symbol
- source component
- correlation id
- input event reference
- output decision or state transition
- error/reason when applicable

Audit records must be sufficient to explain why an order was accepted, rejected, held for review, cancelled, filled, or reconciled.

## Failure Posture

When market/account data is stale, exchange state is inconsistent, or reconciliation cannot prove correctness, the system must avoid new risk. Acceptable responses include halting new orders, reducing exposure, cancelling open orders, or requiring operator review according to `docs/RISK_POLICY.md`.
