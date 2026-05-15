"""Validation helpers for exchange-independent domain models."""

import re
from collections.abc import Mapping
from datetime import datetime
from decimal import Decimal
from types import MappingProxyType

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


def normalized_metadata_key(key: str) -> str:
    key_with_separators = key.replace("-", "_")
    split_acronyms = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", key_with_separators)
    split_camel = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", split_acronyms)
    return re.sub(r"_+", "_", split_camel).lower()


def ensure_metadata_values_are_primitive(metadata: Mapping[str, object]) -> None:
    for value in metadata.values():
        if not isinstance(value, str | int | Decimal | bool):
            raise ValueError("metadata values must be primitive")


def metadata_without_exchange_payload(
    metadata: Mapping[str, MetadataValue],
) -> Mapping[str, MetadataValue]:
    forbidden_keys = FORBIDDEN_METADATA_KEYS.intersection(
        normalized_metadata_key(key) for key in metadata
    )
    if forbidden_keys:
        raise ValueError("metadata must not contain exchange-specific payload keys")
    ensure_metadata_values_are_primitive(metadata)
    return MappingProxyType(dict(metadata))


def safe_metadata(metadata: Mapping[str, MetadataValue]) -> Mapping[str, MetadataValue]:
    return metadata_without_exchange_payload(metadata)
