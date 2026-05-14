# Exchange Adapter Spec

## Purpose

Exchange adapter는 core system과 external exchange 사이의 translation boundary이다. 초기 adapter는 BingX USDT perpetual futures를 대상으로 하지만, contract는 future exchanges를 수용할 수 있어야 한다.

## Location Rule

BingX-specific implementation must live only under:

```text
adapters/exchanges/bingx
```

No core module may import BingX-specific types, clients, response payloads, or authentication helpers.

## Adapter Responsibilities

Adapter may:

- translate exchange-neutral order commands into BingX requests;
- translate BingX responses into exchange-neutral events;
- manage REST/WebSocket connectivity;
- normalize market data, account data, order status, fills, funding, fees, leverage, and margin information;
- provide exchange state snapshots for reconciliation.

Adapter must not:

- make strategy decisions;
- override `RiskDecision`;
- create orders without `OMS` command;
- store or print secrets;
- expose raw credential values in logs, errors, tests, docs, or telemetry.

## Public Repository Safety

- Real API key, secret, token, account id, or exchange account details must never appear in adapter code, docs, tests, or fixtures.
- `.env` must not be committed.
- `.env.example` is the only allowed environment template.
- API keys must have withdrawal permission disabled.
- Runtime credential loading must fail closed when required live/demo credentials are missing or ambiguous.

## Required Capabilities

The adapter contract should eventually support:

- market data subscription and snapshots;
- account and position data subscription/snapshots;
- order submit/cancel/query;
- order status normalization;
- fill normalization;
- leverage and margin mode query/update where supported;
- fee and funding reporting;
- exchange clock/time synchronization metadata;
- reconnect and resubscribe behavior;
- rate limit and retry metadata.

## Failure Handling

Adapter failures are domain events, not just logs.

- REST API outage must emit an error event and trigger risk-aware behavior.
- WebSocket disconnect must mark dependent data streams as stale until recovered.
- Delayed market/account data must be visible to `Risk Engine` and `Reconciliation`.
- Unknown order status must not be silently treated as cancelled or filled.
- Duplicate/out-of-order exchange events must be handled idempotently.

## Reconciliation Contract

Adapter must provide enough data to compare exchange actual state with internal state:

- open orders;
- recent orders and fills;
- positions;
- balances/margin;
- leverage and margin mode;
- funding and fee history where available.

When exchange state cannot be fetched reliably, reconciliation must report uncertainty rather than fabricate consistency.
