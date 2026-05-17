"""Exchange-independent domain event contracts."""

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime

from trading_system.core.domain.validation import (
    MetadataValue,
    ensure_timezone_aware,
    safe_metadata,
)

EVENT_TYPE_PATTERN = re.compile(r"^[a-z][a-z0-9]*(\.[a-z][a-z0-9]*)+$")


def ensure_non_blank(name: str, value: str) -> str:
    if not value.strip():
        raise ValueError(f"{name} must not be blank")
    return value


def ensure_event_type(value: str) -> str:
    ensure_non_blank("event_type", value)
    if EVENT_TYPE_PATTERN.fullmatch(value) is None:
        raise ValueError("event_type must use lowercase dotted names")
    return value


def safe_event_data(data: Mapping[str, MetadataValue]) -> Mapping[str, MetadataValue]:
    try:
        return safe_metadata(data)
    except ValueError as error:
        if str(error) == "metadata values must be primitive":
            raise ValueError("data values must be primitive") from error
        raise ValueError("data must not contain exchange-specific keys") from error


@dataclass(frozen=True, slots=True)
class DomainEvent:
    event_id: str
    event_type: str
    occurred_at: datetime
    subject: str
    data: Mapping[str, MetadataValue] = field(default_factory=dict)
    correlation_id: str | None = None
    causation_id: str | None = None
    metadata: Mapping[str, MetadataValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_id", ensure_non_blank("event_id", self.event_id))
        object.__setattr__(self, "event_type", ensure_event_type(self.event_type))
        object.__setattr__(self, "subject", ensure_non_blank("subject", self.subject))
        ensure_timezone_aware("occurred_at", self.occurred_at)
        if self.correlation_id is not None:
            object.__setattr__(
                self,
                "correlation_id",
                ensure_non_blank("correlation_id", self.correlation_id),
            )
        if self.causation_id is not None:
            object.__setattr__(
                self,
                "causation_id",
                ensure_non_blank("causation_id", self.causation_id),
            )
        object.__setattr__(self, "data", safe_event_data(self.data))
        object.__setattr__(self, "metadata", safe_metadata(self.metadata))
