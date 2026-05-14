# Risk Policy

## Policy Intent

`Risk Engine` protects capital and system integrity. It has final authority over strategy output, AI/ML suggestions, OMS requests, configuration, and operator commands.

## Default Posture

- Default execution mode is `paper`.
- Live trading is disabled unless `docs/LIVE_TRADING_GATE.md` conditions pass.
- Risk-increasing action is rejected when state is stale, uncertain, unreconciled, or outside configured limits.
- Conservative behavior is preferred over continued trading under ambiguity.

## Required Controls

- `KillSwitch`: global and scoped ability to block new orders and optionally cancel open orders.
- `MaxLossLimit`: daily/session/account/symbol loss limits before risk-increasing orders are blocked.
- `MaxPositionLimit`: maximum exposure per symbol and account context.
- `MaxOrderSize`: maximum single order notional/quantity.
- `LeverageLimit`: allowed leverage range by mode/symbol.
- `MarginModePolicy`: explicit handling for `isolated` and `cross` margin.
- `LiquidationRiskCheck`: reject or reduce orders that move liquidation risk beyond allowed threshold.
- `StaleDataGuard`: block decisions when market/account data freshness is outside tolerance.
- `ReconciliationGuard`: block risk-increasing action when internal and exchange state disagree materially.
- `LiveTradingGuard`: final gate that blocks live orders unless all live conditions are satisfied.

## Futures-Specific Risk

Risk evaluation must consider:

- leverage and effective leverage;
- isolated versus cross margin behavior;
- entry price and mark price;
- liquidation distance/risk;
- unrealized and realized PnL;
- fees, funding fees, and slippage;
- partial fills and remaining exposure;
- open orders that may increase exposure.

## Decision Outcomes

`RiskDecision` may be:

- `approved`: intent may proceed to `OMS`.
- `rejected`: intent is blocked with `RiskReason`.
- `modified`: intent may proceed only with risk-approved constraints.
- `requires_review`: no automatic order submission until operator review.

## Kill Switch Behavior

When kill switch is active:

- new risk-increasing orders are rejected;
- live mode must not submit new orders;
- open order cancellation may be allowed if it reduces risk;
- position-reducing actions may require stricter policy depending on system state.

## Failure Policy

These conditions must trigger conservative behavior:

- exchange API outage;
- WebSocket disconnect;
- delayed market/account data;
- order state mismatch;
- position mismatch;
- unknown partial-fill state;
- reconciliation drift;
- restart recovery not yet complete.

The system must record the risk decision and reason every time it blocks, modifies, or requires review.
