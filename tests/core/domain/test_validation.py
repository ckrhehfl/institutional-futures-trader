from datetime import UTC, datetime
from decimal import Decimal
from types import MappingProxyType

import pytest

from trading_system.core.domain.validation import (
    FORBIDDEN_METADATA_KEYS,
    ensure_non_negative_decimal,
    ensure_positive_decimal,
    ensure_timezone_aware,
    metadata_without_exchange_payload,
)


def test_decimal_validation_rejects_invalid_values() -> None:
    assert ensure_positive_decimal("quantity", Decimal("0.1")) == Decimal("0.1")
    assert ensure_non_negative_decimal("fee", Decimal("0")) == Decimal("0")

    with pytest.raises(ValueError, match="quantity must be positive"):
        ensure_positive_decimal("quantity", Decimal("0"))

    with pytest.raises(ValueError, match="fee must be non-negative"):
        ensure_non_negative_decimal("fee", Decimal("-0.01"))


def test_decimal_validation_rejects_non_finite_values() -> None:
    for value in [Decimal("Infinity"), Decimal("-Infinity"), Decimal("NaN")]:
        with pytest.raises(ValueError, match="quantity must be finite"):
            ensure_positive_decimal("quantity", value)

        with pytest.raises(ValueError, match="fee must be finite"):
            ensure_non_negative_decimal("fee", value)


def test_timezone_validation_requires_aware_datetime() -> None:
    aware = datetime(2026, 5, 15, tzinfo=UTC)
    assert ensure_timezone_aware("created_at", aware) == aware

    with pytest.raises(ValueError, match="created_at must be timezone-aware"):
        ensure_timezone_aware("created_at", datetime(2026, 5, 15))


def test_metadata_rejects_exchange_specific_payloads() -> None:
    assert "bingx" in FORBIDDEN_METADATA_KEYS
    metadata = metadata_without_exchange_payload({"source": "paper"})
    assert metadata == {"source": "paper"}
    assert isinstance(metadata, MappingProxyType)

    for key in ["raw", "payload", "response", "bingx", "exchange_response", "api_key"]:
        with pytest.raises(ValueError, match="metadata must not contain exchange-specific"):
            metadata_without_exchange_payload({key: "not allowed"})


def test_metadata_rejects_secret_key_spelling_variants() -> None:
    for key in [
        "api-key",
        "apiKey",
        "APIKey",
        "API_KEY",
        "account-id",
        "accountId",
        "ACCOUNT_ID",
        "exchangeResponse",
    ]:
        with pytest.raises(ValueError, match="metadata must not contain exchange-specific"):
            metadata_without_exchange_payload({key: "not allowed"})


def test_metadata_rejects_non_primitive_values() -> None:
    for metadata in [
        {"context": {"safe_nested_key": "not allowed"}},
        {"items": ["nested item"]},
        {"value": object()},
    ]:
        with pytest.raises(ValueError, match="metadata values must be primitive"):
            metadata_without_exchange_payload(metadata)
