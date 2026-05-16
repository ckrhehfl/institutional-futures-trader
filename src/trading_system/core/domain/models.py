"""Exchange-independent frozen domain models."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from trading_system.core.domain.enums import (
    ExecutionVenue,
    MarginMode,
    OrderSide,
    OrderStatus,
    OrderType,
    PositionMode,
    PositionSide,
    ReconciliationStatus,
    RiskDecisionStatus,
    TimeInForce,
    TradingMode,
)
from trading_system.core.domain.validation import (
    MetadataValue,
    ensure_finite_decimal,
    ensure_non_negative_decimal,
    ensure_positive_decimal,
    ensure_timezone_aware,
    safe_metadata,
)

ORDER_INTENT_CREATORS = frozenset(
    {"intent_builder", "order_intent_builder", "portfolio_construction"}
)
SIGNAL_CONFIDENCE_LABELS = frozenset({"low", "medium", "high"})
LIMIT_PRICE_ORDER_TYPES = frozenset({OrderType.LIMIT})
UNSUPPORTED_STOP_ORDER_TYPES = frozenset({OrderType.STOP, OrderType.STOP_LIMIT})
TERMINAL_FILLED_STATUSES = frozenset({OrderStatus.FILLED})
PARTIAL_FILL_STATUSES = frozenset(
    {
        OrderStatus.PARTIALLY_FILLED,
        OrderStatus.CANCELED,
        OrderStatus.EXPIRED,
        OrderStatus.UNKNOWN,
    }
)
PRE_EXECUTION_STATUSES = frozenset(
    {
        OrderStatus.CREATED,
        OrderStatus.RISK_APPROVED,
        OrderStatus.ACCEPTED,
    }
)


@dataclass(frozen=True, slots=True)
class Signal:
    signal_id: str
    symbol: str
    created_at: datetime
    source: str
    confidence: Decimal | str | None = None
    regime: str | None = None
    sizing_suggestion: Decimal | None = None
    metadata: Mapping[str, MetadataValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        ensure_timezone_aware("created_at", self.created_at)
        if self.confidence is not None:
            if isinstance(self.confidence, str):
                if self.confidence not in SIGNAL_CONFIDENCE_LABELS:
                    raise ValueError("confidence label must be low, medium, or high")
            else:
                ensure_non_negative_decimal("confidence", self.confidence)
        if self.sizing_suggestion is not None:
            ensure_non_negative_decimal("sizing_suggestion", self.sizing_suggestion)
        object.__setattr__(self, "metadata", safe_metadata(self.metadata))


@dataclass(frozen=True, slots=True)
class OrderIntent:
    intent_id: str
    source_signal_id: str
    created_by: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    limit_price: Decimal | None
    time_in_force: TimeInForce
    trading_mode: TradingMode
    execution_venue: ExecutionVenue
    leverage: Decimal
    reduce_only: bool
    close_only: bool
    post_only: bool
    created_at: datetime
    metadata: Mapping[str, MetadataValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        side = OrderSide(self.side)
        order_type = OrderType(self.order_type)
        time_in_force = TimeInForce(self.time_in_force)
        trading_mode = TradingMode(self.trading_mode)
        execution_venue = ExecutionVenue(self.execution_venue)
        object.__setattr__(self, "side", side)
        object.__setattr__(self, "order_type", order_type)
        object.__setattr__(self, "time_in_force", time_in_force)
        object.__setattr__(self, "trading_mode", trading_mode)
        object.__setattr__(self, "execution_venue", execution_venue)
        if self.created_by not in ORDER_INTENT_CREATORS:
            raise ValueError("OrderIntent creator must be an intent builder")
        if self.close_only and not self.reduce_only:
            raise ValueError("close-only requires reduce-only")
        ensure_positive_decimal("quantity", self.quantity)
        ensure_positive_decimal("leverage", self.leverage)
        if order_type in UNSUPPORTED_STOP_ORDER_TYPES:
            raise ValueError("stop order types are not supported until trigger_price is modeled")
        if order_type in LIMIT_PRICE_ORDER_TYPES and self.limit_price is None:
            raise ValueError("limit_price is required for priced order types")
        if order_type not in LIMIT_PRICE_ORDER_TYPES and self.limit_price is not None:
            raise ValueError("limit_price is only valid for limit orders")
        if order_type not in LIMIT_PRICE_ORDER_TYPES and (
            time_in_force == TimeInForce.POST_ONLY or self.post_only
        ):
            raise ValueError("post-only is only valid for limit orders")
        if time_in_force == TimeInForce.POST_ONLY and not self.post_only:
            raise ValueError("post-only fields must agree")
        if self.post_only and time_in_force != TimeInForce.POST_ONLY:
            raise ValueError("post-only limit orders must use post-only time in force")
        if self.limit_price is not None:
            ensure_positive_decimal("limit_price", self.limit_price)
        ensure_timezone_aware("created_at", self.created_at)
        self._ensure_mode_matches_venue()
        object.__setattr__(self, "metadata", safe_metadata(self.metadata))

    def _ensure_mode_matches_venue(self) -> None:
        trading_mode = TradingMode(self.trading_mode)
        execution_venue = ExecutionVenue(self.execution_venue)
        if trading_mode == TradingMode.LIVE:
            raise ValueError("live mode is not supported by domain v0")
        expected_venue = {
            TradingMode.BACKTEST: ExecutionVenue.BACKTEST,
            TradingMode.PAPER: ExecutionVenue.PAPER,
            TradingMode.DEMO: ExecutionVenue.DEMO,
        }[trading_mode]
        if execution_venue == expected_venue:
            return
        mode_name = trading_mode.value
        venue_name = expected_venue.value
        raise ValueError(f"{mode_name} mode must use {venue_name} execution venue")


@dataclass(frozen=True, slots=True)
class Order:
    order_id: str
    intent_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    status: OrderStatus
    quantity: Decimal
    filled_quantity: Decimal
    limit_price: Decimal | None
    time_in_force: TimeInForce
    reduce_only: bool
    close_only: bool
    post_only: bool
    created_at: datetime
    updated_at: datetime
    metadata: Mapping[str, MetadataValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        side = OrderSide(self.side)
        order_type = OrderType(self.order_type)
        status = OrderStatus(self.status)
        time_in_force = TimeInForce(self.time_in_force)
        object.__setattr__(self, "side", side)
        object.__setattr__(self, "order_type", order_type)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "time_in_force", time_in_force)
        ensure_positive_decimal("quantity", self.quantity)
        ensure_non_negative_decimal("filled_quantity", self.filled_quantity)
        if self.close_only and not self.reduce_only:
            raise ValueError("close-only requires reduce-only")
        if status == OrderStatus.PENDING_RISK:
            raise ValueError("pre-risk intents must not become orders")
        if status == OrderStatus.RISK_REJECTED:
            raise ValueError("risk-rejected intents must not become orders")
        if self.filled_quantity > self.quantity:
            raise ValueError("filled_quantity must not exceed quantity")
        if status in PRE_EXECUTION_STATUSES and self.filled_quantity != Decimal("0"):
            raise ValueError("pre-execution order states must have zero fills")
        if status == OrderStatus.PARTIALLY_FILLED and not (
            Decimal("0") < self.filled_quantity < self.quantity
        ):
            raise ValueError("partially filled order requires partial filled quantity")
        if status in TERMINAL_FILLED_STATUSES and self.filled_quantity != self.quantity:
            raise ValueError("filled order must have no remaining quantity")
        if (
            status not in PARTIAL_FILL_STATUSES
            and Decimal("0") < self.filled_quantity < self.quantity
        ):
            raise ValueError("partial filled quantity requires partial status")
        if status not in TERMINAL_FILLED_STATUSES and self.filled_quantity == self.quantity:
            raise ValueError("complete filled quantity requires filled status")
        if order_type in UNSUPPORTED_STOP_ORDER_TYPES:
            raise ValueError("stop order types are not supported until trigger_price is modeled")
        if order_type in LIMIT_PRICE_ORDER_TYPES and self.limit_price is None:
            raise ValueError("limit_price is required for priced order types")
        if order_type not in LIMIT_PRICE_ORDER_TYPES and self.limit_price is not None:
            raise ValueError("limit_price is only valid for limit orders")
        if order_type not in LIMIT_PRICE_ORDER_TYPES and (
            time_in_force == TimeInForce.POST_ONLY or self.post_only
        ):
            raise ValueError("post-only is only valid for limit orders")
        if time_in_force == TimeInForce.POST_ONLY and not self.post_only:
            raise ValueError("post-only fields must agree")
        if self.post_only and time_in_force != TimeInForce.POST_ONLY:
            raise ValueError("post-only limit orders must use post-only time in force")
        if self.limit_price is not None:
            ensure_positive_decimal("limit_price", self.limit_price)
        ensure_timezone_aware("created_at", self.created_at)
        ensure_timezone_aware("updated_at", self.updated_at)
        if self.updated_at < self.created_at:
            raise ValueError("updated_at must not predate created_at")
        object.__setattr__(self, "metadata", safe_metadata(self.metadata))

    @property
    def remaining_quantity(self) -> Decimal:
        return self.quantity - self.filled_quantity


@dataclass(frozen=True, slots=True)
class Fill:
    fill_id: str
    order_id: str
    symbol: str
    side: OrderSide
    quantity: Decimal
    price: Decimal
    fee: Decimal
    filled_at: datetime
    metadata: Mapping[str, MetadataValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        side = OrderSide(self.side)
        object.__setattr__(self, "side", side)
        ensure_positive_decimal("quantity", self.quantity)
        ensure_positive_decimal("price", self.price)
        ensure_non_negative_decimal("fee", self.fee)
        ensure_timezone_aware("filled_at", self.filled_at)
        object.__setattr__(self, "metadata", safe_metadata(self.metadata))

    @property
    def notional(self) -> Decimal:
        return self.quantity * self.price


@dataclass(frozen=True, slots=True)
class Fee:
    symbol: str
    amount: Decimal
    asset: str
    occurred_at: datetime
    metadata: Mapping[str, MetadataValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        ensure_non_negative_decimal("amount", self.amount)
        ensure_timezone_aware("occurred_at", self.occurred_at)
        object.__setattr__(self, "metadata", safe_metadata(self.metadata))


@dataclass(frozen=True, slots=True)
class FundingFee:
    symbol: str
    amount: Decimal
    asset: str
    funding_timestamp: datetime
    occurred_at: datetime
    metadata: Mapping[str, MetadataValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        ensure_finite_decimal("amount", self.amount)
        ensure_timezone_aware("funding_timestamp", self.funding_timestamp)
        ensure_timezone_aware("occurred_at", self.occurred_at)
        object.__setattr__(self, "metadata", safe_metadata(self.metadata))


@dataclass(frozen=True, slots=True)
class PnL:
    symbol: str
    realized: Decimal
    unrealized: Decimal
    fees: Decimal
    funding: Decimal
    updated_at: datetime
    metadata: Mapping[str, MetadataValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        ensure_finite_decimal("realized", self.realized)
        ensure_finite_decimal("unrealized", self.unrealized)
        ensure_non_negative_decimal("fees", self.fees)
        ensure_finite_decimal("funding", self.funding)
        ensure_timezone_aware("updated_at", self.updated_at)
        object.__setattr__(self, "metadata", safe_metadata(self.metadata))


@dataclass(frozen=True, slots=True)
class Position:
    symbol: str
    side: PositionSide
    quantity: Decimal
    entry_price: Decimal | None
    mark_price: Decimal
    leverage: Decimal
    margin_mode: MarginMode
    position_mode: PositionMode
    maintenance_margin: Decimal
    liquidation_price: Decimal | None
    updated_at: datetime
    metadata: Mapping[str, MetadataValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        side = PositionSide(self.side)
        margin_mode = MarginMode(self.margin_mode)
        position_mode = PositionMode(self.position_mode)
        object.__setattr__(self, "side", side)
        object.__setattr__(self, "margin_mode", margin_mode)
        object.__setattr__(self, "position_mode", position_mode)
        ensure_non_negative_decimal("quantity", self.quantity)
        if side == PositionSide.FLAT:
            if self.quantity != Decimal("0"):
                raise ValueError("flat position quantity must be zero")
            if self.entry_price not in {None, Decimal("0")}:
                raise ValueError("flat position entry_price must be absent or zero")
            if self.maintenance_margin != Decimal("0"):
                raise ValueError("flat position maintenance_margin must be zero")
            if self.liquidation_price is not None:
                raise ValueError("flat position liquidation_price must be absent")
        else:
            if self.quantity == Decimal("0"):
                raise ValueError("non-flat position quantity must be positive")
            if self.entry_price is None:
                raise ValueError("entry_price is required for open positions")
            ensure_positive_decimal("entry_price", self.entry_price)
        ensure_positive_decimal("mark_price", self.mark_price)
        ensure_positive_decimal("leverage", self.leverage)
        ensure_non_negative_decimal("maintenance_margin", self.maintenance_margin)
        if self.liquidation_price is not None:
            ensure_positive_decimal("liquidation_price", self.liquidation_price)
        ensure_timezone_aware("updated_at", self.updated_at)
        object.__setattr__(self, "metadata", safe_metadata(self.metadata))


@dataclass(frozen=True, slots=True)
class RiskDecision:
    decision_id: str
    intent_id: str
    status: RiskDecisionStatus
    reason: str
    decided_at: datetime
    metadata: Mapping[str, MetadataValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        status = RiskDecisionStatus(self.status)
        object.__setattr__(self, "status", status)
        if not self.reason.strip():
            raise ValueError("reason must not be blank")
        ensure_timezone_aware("decided_at", self.decided_at)
        object.__setattr__(self, "metadata", safe_metadata(self.metadata))


@dataclass(frozen=True, slots=True)
class ReconciliationEvent:
    event_id: str
    status: ReconciliationStatus
    symbol: str
    occurred_at: datetime
    internal_state_ref: str
    exchange_snapshot_ref: str
    drift_summary: str
    requires_manual_review: bool
    metadata: Mapping[str, MetadataValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        status = ReconciliationStatus(self.status)
        object.__setattr__(self, "status", status)
        if status == ReconciliationStatus.REQUIRES_REVIEW and not self.requires_manual_review:
            raise ValueError("requires_manual_review must be true when status requires review")
        ensure_timezone_aware("occurred_at", self.occurred_at)
        object.__setattr__(self, "metadata", safe_metadata(self.metadata))
