from datetime import UTC, datetime

import pytest

from trading_system.core.domain import DomainEvent

NOW = datetime(2026, 5, 17, 9, 0, tzinfo=UTC)


def test_domain_event_records_exchange_independent_fact_without_runtime_behavior() -> None:
    event = DomainEvent(
        event_id="evt-1",
        event_type="signal.generated",
        occurred_at=NOW,
        subject="signal-1",
        data={"symbol": "BTC-USDT", "source": "mean_reversion"},
        correlation_id="corr-1",
        causation_id="signal-1",
        metadata={"trace": "domain-v0"},
    )

    assert event.event_type == "signal.generated"
    assert event.subject == "signal-1"
    assert event.data["symbol"] == "BTC-USDT"
    assert event.correlation_id == "corr-1"
    assert event.causation_id == "signal-1"
    assert not hasattr(event, "publish")
    assert not hasattr(event, "subscribe")
    assert not hasattr(event, "dispatch")
    assert not hasattr(event, "save")

    with pytest.raises(TypeError):
        event.data["symbol"] = "ETH-USDT"  # type: ignore[index]


def test_domain_event_rejects_exchange_payload_or_secret_bearing_data() -> None:
    for forbidden_data in [
        {"raw_payload": "{}"},
        {"exchange_response": "ok"},
        {"account_id": "acct-1"},
        {"api_key": "not-a-real-key"},  # pragma: allowlist secret
    ]:
        with pytest.raises(ValueError, match="data must not contain exchange-specific"):
            DomainEvent(
                event_id="evt-1",
                event_type="order.intent.created",
                occurred_at=NOW,
                subject="intent-1",
                data=forbidden_data,
                metadata={},
            )


def test_domain_event_data_values_must_be_primitive() -> None:
    with pytest.raises(ValueError, match="data values must be primitive"):
        DomainEvent(
            event_id="evt-1",
            event_type="signal.generated",
            occurred_at=NOW,
            subject="signal-1",
            data={"nested": {"not": "allowed"}},  # type: ignore[dict-item]
            metadata={},
        )


def test_domain_event_rejects_exchange_payload_or_secret_bearing_metadata() -> None:
    with pytest.raises(ValueError, match="metadata must not contain exchange-specific"):
        DomainEvent(
            event_id="evt-1",
            event_type="risk.decision.recorded",
            occurred_at=NOW,
            subject="risk-1",
            data={"status": "requires_review"},
            metadata={"exchange_payload": "not allowed"},
        )


def test_domain_event_requires_timezone_aware_occurred_at() -> None:
    with pytest.raises(ValueError, match="occurred_at must be timezone-aware"):
        DomainEvent(
            event_id="evt-1",
            event_type="position.updated",
            occurred_at=datetime(2026, 5, 17, 9, 0),
            subject="position-1",
            data={"symbol": "BTC-USDT"},
            metadata={},
        )


def test_domain_event_requires_stable_identifiers_and_type_name() -> None:
    invalid_examples = [
        {"event_id": "", "event_type": "signal.generated", "subject": "signal-1"},
        {"event_id": "evt-1", "event_type": "", "subject": "signal-1"},
        {"event_id": "evt-1", "event_type": "SignalGenerated", "subject": "signal-1"},
        {"event_id": "evt-1", "event_type": "signal generated", "subject": "signal-1"},
        {"event_id": "evt-1", "event_type": "signal.generated", "subject": ""},
    ]

    for example in invalid_examples:
        with pytest.raises(ValueError):
            DomainEvent(
                event_id=example["event_id"],
                event_type=example["event_type"],
                occurred_at=NOW,
                subject=example["subject"],
                data={},
                metadata={},
            )
