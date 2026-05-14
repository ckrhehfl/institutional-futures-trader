# Order Lifecycle

## Purpose

This lifecycle defines how an idea becomes an order, how an order becomes execution, and how execution updates position, PnL, and reconciliation state.

## Lifecycle Stages

1. `SignalCreated`
   - Strategy or advisory module emits a `Signal`.
   - A `Signal` is not executable and cannot reach the exchange.

2. `OrderIntentCreated`
   - Strategy or sizing logic creates an `OrderIntent`.
   - Intent includes source, symbol, side, size, price constraints, leverage/margin assumptions, and rationale.

3. `RiskEvaluated`
   - `Risk Engine` evaluates the intent.
   - Output is `RiskDecision`: approved, rejected, modified, or requires_review.

4. `OrderAcceptedByOMS`
   - Only risk-approved intent can become an `Order`.
   - `OMS` assigns identity, correlation id, and initial lifecycle state.

5. `OrderSubmitted`
   - `OMS` sends an exchange-neutral command to the exchange adapter.
   - Adapter translates the command to BingX only inside `adapters/exchanges/bingx`.

6. `ExchangeAcknowledged`
   - Exchange acceptance/rejection is normalized into an event.
   - Unknown status remains unknown until resolved; it is not guessed.

7. `FillReceived`
   - Full or partial fills update order state.
   - Fees, slippage, execution price, and fill quantity are recorded.

8. `PositionAndPnLUpdated`
   - Position, entry price, mark-price-based unrealized PnL, realized PnL, fee, funding, and liquidation risk are updated.

9. `Reconciled`
   - Internal state is compared with exchange actual state.
   - Mismatches become `ReconciliationEvent` and may trigger risk controls.

## Partial Fills

Partial fill handling must:

- preserve remaining quantity;
- update realized/unrealized exposure accurately;
- account for fees and slippage per fill;
- avoid duplicate processing;
- keep order state distinct from fully filled or cancelled.

## Mismatches

Order state mismatch or position mismatch must be treated as a first-class event. The system must not silently assume the most convenient state.

Examples:

- internal order is open but exchange reports filled;
- internal order is submitted but exchange has no record;
- exchange position quantity differs from internal position;
- fill arrives after reconnect or restart;
- cancellation result is unknown.

## Restart Recovery

After restart, the system must:

- rebuild internal state from durable event/state records;
- fetch exchange snapshots where applicable;
- reconcile open orders, positions, balances, leverage, and margin mode;
- block new risk-increasing orders until recovery and reconciliation are complete.

## Audit Requirements

Every lifecycle transition must be recorded with timestamp, mode, symbol, correlation id, source, prior state, new state, and reason/error when applicable.
