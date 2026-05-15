"""Validation helpers for exchange-independent domain models."""

from collections.abc import Mapping
from datetime import datetime
from decimal import Decimal

MetadataValue = str | int | Decimal | bool

FORBIDDEN_METADATA_KEYS = frozenset(
    {
        "raw",
        "payload",
        "response",
        "exchange_response",
        "bingx",
        "error_code",
        "account_id",
        "api_key",
        "secret",
        "token",
    }
)


def ensure_positive_decimal(name: str, value: Decimal) -> Decimal:
    if value <= Decimal("0"):
        raise ValueError(f"{name} must be positive")
    return value


def ensure_non_negative_decimal(name: str, value: Decimal) -> Decimal:
    if value < Decimal("0"):
        raise ValueError(f"{name} must be non-negative")
    return value


def ensure_timezone_aware(name: str, value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value


def metadata_without_exchange_payload(
    metadata: Mapping[str, MetadataValue],
) -> dict[str, MetadataValue]:
    forbidden_keys = FORBIDDEN_METADATA_KEYS.intersection(key.lower() for key in metadata)
    if forbidden_keys:
        raise ValueError("metadata must not contain exchange-specific payload keys")
    return dict(metadata)
