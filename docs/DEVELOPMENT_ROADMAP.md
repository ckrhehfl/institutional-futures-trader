# Development Roadmap

## Phase 0: Documentation Foundation

Create and maintain the project constitution and domain docs. This phase does not include trading engine, BingX API client, strategy code, ML code, or scaffold implementation.

Deliverables:

- repository safety rules;
- architecture boundaries;
- domain model;
- exchange adapter contract;
- risk policy;
- order lifecycle;
- live trading gate.

## Phase 1: Core Domain And Event Model

Implement exchange-independent domain types and event contracts. This phase must stay independent of BingX API shapes.

Required test-first areas:

- `Risk Engine`
- `OMS`
- `Order Lifecycle`
- `Position/PnL`
- `Reconciliation`

## Phase 2: Backtest Mode

Implement historical replay and deterministic evaluation using the same core domain flow planned for paper/demo/live. Backtest results must include fees, slippage assumptions, funding treatment, PnL, drawdown, and risk decision history.

## Phase 3: Paper Trading

Implement default runtime mode. Paper mode must exercise `Strategy -> Risk Engine -> OMS -> Execution Simulator -> Position/PnL -> Reconciliation` without submitting real exchange orders.

## Phase 4: BingX Demo Trading

Add BingX demo/sandbox adapter behavior after core and paper behavior are tested. Demo must validate connectivity, order lifecycle, reconciliation, and failure handling without live capital.

## Phase 5: Live Trading Gate Preparation

Prepare live path only after paper/demo evidence shows stability, correctness, risk control, and reconciliation quality. Live-related code must include tests before it is accepted.

## Phase 6: Gated Live Trading

Enable live only after `docs/LIVE_TRADING_GATE.md` passes. Live mode must require explicit approval, separate environment variables, runtime confirmation, and non-withdrawal API keys.

## Expansion Path

Future expansion may include:

- more symbols;
- additional USDT perpetual markets;
- other exchanges;
- additional strategy families;
- advisory AI/ML modules;
- other asset classes such as equities.

Expansion must not weaken core boundaries, risk authority, auditability, or live safety.
