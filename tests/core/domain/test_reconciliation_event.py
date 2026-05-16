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

    raw_status_decision = RiskDecision(
        decision_id="risk-2",
        intent_id="intent-1",
        status=RiskDecisionStatus.REQUIRES_REVIEW.value,
        reason="manual review required",
        decided_at=NOW,
        metadata={},
    )
    assert raw_status_decision.status is RiskDecisionStatus.REQUIRES_REVIEW


def test_risk_decision_rejects_unknown_status() -> None:
    with pytest.raises(ValueError):
        RiskDecision(
            decision_id="risk-1",
            intent_id="intent-1",
            status="approvedd",
            reason="bad status",
            decided_at=NOW,
            metadata={},
        )


def test_risk_decision_requires_non_empty_reason() -> None:
    for reason in ["", "   "]:
        with pytest.raises(ValueError, match="reason must not be blank"):
            RiskDecision(
                decision_id="risk-1",
                intent_id="intent-1",
                status=RiskDecisionStatus.REQUIRES_REVIEW,
                reason=reason,
                decided_at=NOW,
                metadata={},
            )


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
    with pytest.raises(TypeError):
        event.metadata["action"] = "mutated"  # type: ignore[index]

    raw_status_event = ReconciliationEvent(
        event_id="recon-raw",
        status=ReconciliationStatus.DRIFT_DETECTED.value,
        symbol="BTC-USDT",
        occurred_at=NOW,
        internal_state_ref="internal-position-1",
        exchange_snapshot_ref="snapshot-1",
        drift_summary="open order mismatch",
        requires_manual_review=True,
        metadata={},
    )
    assert raw_status_event.status is ReconciliationStatus.DRIFT_DETECTED

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


def test_reconciliation_requires_review_status_sets_manual_review_flag() -> None:
    with pytest.raises(ValueError, match="requires_manual_review must be true"):
        ReconciliationEvent(
            event_id="recon-1",
            status=ReconciliationStatus.REQUIRES_REVIEW,
            symbol="BTC-USDT",
            occurred_at=NOW,
            internal_state_ref="internal-position-1",
            exchange_snapshot_ref="snapshot-1",
            drift_summary="manual review required",
            requires_manual_review=False,
            metadata={},
        )


def test_reconciliation_event_rejects_unknown_status() -> None:
    with pytest.raises(ValueError):
        ReconciliationEvent(
            event_id="recon-1",
            status="almost_matched",
            symbol="BTC-USDT",
            occurred_at=NOW,
            internal_state_ref="internal-position-1",
            exchange_snapshot_ref="snapshot-1",
            drift_summary="bad status",
            requires_manual_review=True,
            metadata={},
        )
