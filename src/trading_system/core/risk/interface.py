"""Exchange-independent Risk Engine interface contract."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol

from trading_system.core.domain import OrderIntent, RiskDecision
from trading_system.core.domain.validation import (
    MetadataValue,
    ensure_timezone_aware,
    safe_metadata,
)


def ensure_non_blank(name: str, value: str) -> str:
    if not value.strip():
        raise ValueError(f"{name} must not be blank")
    return value


@dataclass(frozen=True, slots=True)
class RiskEvaluationRequest:
    request_id: str
    order_intent: OrderIntent
    requested_at: datetime
    metadata: Mapping[str, MetadataValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "request_id", ensure_non_blank("request_id", self.request_id))
        if not isinstance(self.order_intent, OrderIntent):
            raise ValueError("order_intent must be an OrderIntent")
        ensure_timezone_aware("requested_at", self.requested_at)
        object.__setattr__(self, "metadata", safe_metadata(self.metadata))


class RiskEngine(Protocol):
    def evaluate(self, request: RiskEvaluationRequest) -> RiskDecision:
        """Evaluate an order intent and return a domain RiskDecision."""
