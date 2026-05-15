"""Exchange-independent frozen domain models."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from trading_system.core.domain.enums import (
    ExecutionVenue,
    OrderSide,
    OrderType,
    TimeInForce,
    TradingMode,
)
from trading_system.core.domain.validation import (
    MetadataValue,
    ensure_positive_decimal,
    ensure_timezone_aware,
    metadata_without_exchange_payload,
)

ORDER_INTENT_CREATORS = frozenset(
    {"intent_builder", "order_intent_builder", "portfolio_construction"}
)


@dataclass(frozen=True, slots=True)
class Signal:
    signal_id: str
    symbol: str
    created_at: datetime
    source: str
    confidence: Decimal | None = None
    regime: str | None = None
    sizing_suggestion: Decimal | None = None
    metadata: Mapping[str, MetadataValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        ensure_timezone_aware("created_at", self.created_at)
        if self.confidence is not None:
            ensure_positive_decimal("confidence", self.confidence)
        if self.sizing_suggestion is not None:
            ensure_positive_decimal("sizing_suggestion", self.sizing_suggestion)
        object.__setattr__(self, "metadata", metadata_without_exchange_payload(self.metadata))


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
        if self.created_by not in ORDER_INTENT_CREATORS:
            raise ValueError("OrderIntent creator must be an intent builder")
        ensure_positive_decimal("quantity", self.quantity)
        ensure_positive_decimal("leverage", self.leverage)
        if self.limit_price is not None:
            ensure_positive_decimal("limit_price", self.limit_price)
        ensure_timezone_aware("created_at", self.created_at)
        self._ensure_mode_matches_venue()
        object.__setattr__(self, "metadata", metadata_without_exchange_payload(self.metadata))

    def _ensure_mode_matches_venue(self) -> None:
        if self.trading_mode is TradingMode.LIVE:
            raise ValueError("live mode is not supported by domain v0")
        expected_venue = {
            TradingMode.BACKTEST: ExecutionVenue.BACKTEST,
            TradingMode.PAPER: ExecutionVenue.PAPER,
            TradingMode.DEMO: ExecutionVenue.DEMO,
        }[self.trading_mode]
        if self.execution_venue is expected_venue:
            return
        mode_name = self.trading_mode.value
        venue_name = expected_venue.value
        raise ValueError(f"{mode_name} mode must use {venue_name} execution venue")
