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
        "error_code",
        "account_id",
        "api_key",
        "secret",
        "token",
    }
)
FORBIDDEN_METADATA_TOKENS = frozenset(
    {
        "account",
        "address",
        "api",
        "exchange",
        "payload",
        "raw",
        "response",
        "secret",
        "token",
        "wallet",
        "withdrawal",
    }
)
FORBIDDEN_COMPACT_METADATA_KEYS = frozenset(
    {
        "accountid",
        "accesstoken",
        "apikey",
        "apisecret",
        "secretkey",
        "walletaddress",
        "withdrawaladdress",
    }
)
FORBIDDEN_COMPACT_METADATA_SUBSTRINGS = frozenset(
    {
        "accountid",
        "accesstoken",
        "apikey",
        "apisecret",
        "secretkey",
        "walletaddress",
        "withdrawaladdress",
    }
)


def ensure_positive_decimal(name: str, value: Decimal) -> Decimal:
    if not value.is_finite():
        raise ValueError(f"{name} must be finite")
    if value <= Decimal("0"):
        raise ValueError(f"{name} must be positive")
    return value


def ensure_non_negative_decimal(name: str, value: Decimal) -> Decimal:
    if not value.is_finite():
        raise ValueError(f"{name} must be finite")
    if value < Decimal("0"):
        raise ValueError(f"{name} must be non-negative")
    return value


def ensure_finite_decimal(name: str, value: Decimal) -> Decimal:
    if not value.is_finite():
        raise ValueError(f"{name} must be finite")
    return value


def ensure_timezone_aware(name: str, value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value


def normalized_metadata_key(key: str) -> str:
    key_with_separators = re.sub(r"[^0-9A-Za-z]+", "_", key)
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
    normalized_keys = {normalized_metadata_key(key) for key in metadata}
    compact_keys = {key.replace("_", "") for key in normalized_keys}
    forbidden_keys = FORBIDDEN_METADATA_KEYS.intersection(normalized_keys)
    forbidden_compact_keys = FORBIDDEN_COMPACT_METADATA_KEYS.intersection(compact_keys)
    forbidden_compact_substrings = {
        substring
        for key in compact_keys
        for substring in FORBIDDEN_COMPACT_METADATA_SUBSTRINGS
        if substring in key
    }
    forbidden_tokens = {token for key in normalized_keys for token in key.split("_")}.intersection(
        FORBIDDEN_METADATA_TOKENS
    )
    if forbidden_keys or forbidden_compact_keys or forbidden_compact_substrings or forbidden_tokens:
        raise ValueError("metadata must not contain exchange-specific payload keys")
    ensure_metadata_values_are_primitive(metadata)
    return MappingProxyType(dict(metadata))


def safe_metadata(metadata: Mapping[str, MetadataValue]) -> Mapping[str, MetadataValue]:
    return metadata_without_exchange_payload(metadata)
