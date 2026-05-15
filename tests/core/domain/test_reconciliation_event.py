from datetime import UTC, datetime

import pytest

from trading_system.core.domain import (
    ReconciliationEvent,
    ReconciliationStatus,
    RiskDecision,
    RiskDecisionStatus,
)

NOW = datetime(2026, 5, 15, 12, 0, tzinfo=UTC)


def test_risk_decision_has_no_order_execution_behavior() -> None:
    decision = RiskDecision(
        decision_id="risk-1",
        intent_id="intent-1",
        status=RiskDecisionStatus.REQUIRES_REVIEW,
        reason="manual review required",
        decided_at=NOW,
        metadata={"policy": "live_guard"},
    )

    assert decision.status is RiskDecisionStatus.REQUIRES_REVIEW
    assert not hasattr(decision, "submit")
    assert not hasattr(decision, "execute")


def test_reconciliation_event_records_drift_without_raw_payload() -> None:
    event = ReconciliationEvent(
        event_id="recon-1",
        status=ReconciliationStatus.DRIFT_DETECTED,
        symbol="BTC-USDT",
        occurred_at=NOW,
        internal_state_ref="internal-position-1",
        exchange_snapshot_ref="snapshot-1",
        drift_summary="open order mismatch",
        requires_manual_review=True,
        metadata={"action": "cancel_open_orders"},
    )

    assert event.requires_manual_review is True

    with pytest.raises(ValueError, match="metadata must not contain exchange-specific"):
        ReconciliationEvent(
            event_id="recon-2",
            status=ReconciliationStatus.DRIFT_DETECTED,
            symbol="BTC-USDT",
            occurred_at=NOW,
            internal_state_ref="internal-position-1",
            exchange_snapshot_ref="snapshot-1",
            drift_summary="bad metadata",
            requires_manual_review=True,
            metadata={"bingx": "not allowed"},
        )
