# Domain Model

이 문서는 구현 언어와 무관한 core domain concepts를 정의한다. 이름은 future implementation에서 stable interface vocabulary로 사용한다.

## Market And Signal

- `Symbol`: exchange-neutral tradable instrument identifier. Initial symbol is `BTC-USDT perpetual`.
- `MarketDataEvent`: trade, candle, order book, mark price, funding, or derived market update.
- `Signal`: strategy output describing directional or neutral intent. It is not an order.
- `SignalConfidence`: optional confidence score or qualitative label, including AI-assisted confidence.
- `Regime`: optional market regime label such as trend, range, volatile, illiquid.
- `AdvisorySuggestion`: non-binding AI/ML or analytics output such as confidence, anomaly, regime, or sizing suggestion.
- `IntentBuilder` / `OrderIntentBuilder`: component that converts signal context and portfolio constraints into `OrderIntent`.

## Order Intent And Risk

- `OrderIntent`: desired trading action before risk approval. It may include symbol, side, size, order type, price constraint, leverage/margin assumptions, reason, and source.
- `RiskDecision`: `approved`, `rejected`, or `requires_review` decision produced by `Risk Engine`.
- `RiskReason`: machine-readable reason explaining the decision.
- `KillSwitchState`: global or scoped state that blocks risk-increasing actions.

## Order And Execution

- `Order`: OMS-owned representation of an accepted order.
- `OrderState`: lifecycle state such as pending, accepted, submitted, partially_filled, filled, cancelled, rejected, expired, unknown.
- `OrderConstraint`: execution constraint such as `reduce_only`, `close_only`, `post_only`, or `time_in_force`.
- `Fill`: execution event with quantity, price, fee, liquidity role when available, and exchange timestamp.
- `PartialFill`: fill that closes only part of the remaining order quantity.
- `Slippage`: difference between intended/reference price and realized execution price.
- `Fee`: trading fee or exchange fee applied to an order/fill.
- `FundingFee`: periodic perpetual futures funding payment or receipt.

## Position And PnL

- `Position`: current exposure by symbol, side/net quantity, entry price, leverage, margin mode, margin usage, and liquidation risk.
- `EntryPrice`: average effective price of the current position.
- `MarkPrice`: exchange/reference price used for unrealized PnL and liquidation risk.
- `UnrealizedPnL`: mark-to-market profit/loss for open exposure.
- `RealizedPnL`: closed profit/loss after fills, fees, funding, and slippage effects.
- `LiquidationRisk`: risk indicator derived from leverage, margin mode, mark price, maintenance margin, and exchange rules.
- `MarginMode`: `isolated` or `cross`.
- `Leverage`: leverage setting or effective leverage for a position/order context.
- `PositionMode`: one-way or hedge position accounting mode.
- `InstrumentRules`: exchange-normalized constraints such as tick size, step size, min notional, max leverage, and supported order flags.
- `MaintenanceMargin`: margin requirement used for liquidation risk and risk limits.
- `DeleveragingRisk`: ADL or forced deleveraging risk indicator when provided or derivable.

## Reconciliation And Recovery

- `ExchangeStateSnapshot`: observed exchange state for orders, balances, positions, leverage, margin, and account data.
- `InternalStateSnapshot`: system's current state derived from event history and persisted state.
- `ReconciliationEvent`: comparison result between internal state and exchange state.
- `ReconciliationDrift`: mismatch requiring correction, halt, or operator review.
- `RecoveryEvent`: restart/rebuild event used to restore state from durable records and exchange snapshots.

## Invariants

- `Signal` is never an order.
- Strategy output must not create executable orders or exchange commands.
- `OrderIntent` is created only by `IntentBuilder` or equivalent portfolio construction component.
- AI/ML output is advisory and must not create `OrderIntent`.
- `OrderIntent` is not executable until approved by `Risk Engine`.
- `OMS` owns order lifecycle state.
- Exchange adapter reports facts; it does not make strategy or risk decisions.
- AI/ML advisory output cannot bypass `Risk Engine` or `OMS`.
