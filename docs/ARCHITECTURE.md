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
        |      Signal / Sizing Suggestion
        |          |
        v          v
Risk Engine -> RiskDecision
        |
        v
OMS -> Order Command
        |
        v
Exchange Adapter -> BingX
        |
        v
Fill / Account Event / Reconciliation Event
```

## Core Boundaries

Core modules must not depend on BingX-specific API shapes.

- `Strategy`: consumes market/domain events and emits `Signal` or `OrderIntent`.
- `AI/ML`: emits advisory metadata only, such as confidence, regime, anomaly, or sizing suggestion.
- `Risk Engine`: validates or rejects every `OrderIntent`.
- `OMS`: owns order state transitions after risk approval.
- `Portfolio/Position`: tracks exposure, margin, PnL, fees, and funding.
- `Reconciliation`: compares internal state with exchange actual state.
- `Exchange Adapter`: translates core commands/events to exchange-specific APIs.

## Exchange Boundary

BingX-specific code must live only under:

```text
adapters/exchanges/bingx
```

Core must communicate with adapters through stable exchange-neutral contracts. Strategy, AI, Risk Engine, OMS, and Portfolio modules must not import BingX client code.

## Mode Parity

`paper`, `demo`, and `live` should share the same event, risk, OMS, position, and reconciliation path. Differences should be isolated at execution/account data boundaries.

The default mode is always `paper`. `live` requires the live gate and cannot be enabled by a single config value.

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

Audit records must be sufficient to explain why an order was accepted, rejected, modified, cancelled, filled, or reconciled.

## Failure Posture

When market/account data is stale, exchange state is inconsistent, or reconciliation cannot prove correctness, the system must avoid new risk. Acceptable responses include halting new orders, reducing exposure, cancelling open orders, or requiring operator review according to `docs/RISK_POLICY.md`.
