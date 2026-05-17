from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from trading_system.core.domain import (
    ExecutionVenue,
    OrderIntent,
    OrderSide,
    OrderType,
    RiskDecision,
    RiskDecisionStatus,
    TimeInForce,
    TradingMode,
)
from trading_system.core.risk import RiskEngine, RiskEvaluationRequest

ROOT = Path(__file__).resolve().parents[3]
RISK_ROOT = ROOT / "src" / "trading_system" / "core" / "risk"
NOW = datetime(2026, 5, 17, 12, 0, tzinfo=UTC)


def make_order_intent() -> OrderIntent:
    return OrderIntent(
        intent_id="intent-1",
        source_signal_id="signal-1",
        created_by="intent_builder",
        symbol="BTC-USDT",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("1"),
        limit_price=Decimal("65000"),
        time_in_force=TimeInForce.GTC,
        trading_mode=TradingMode.PAPER,
        execution_venue=ExecutionVenue.PAPER,
        leverage=Decimal("2"),
        reduce_only=False,
        close_only=False,
        post_only=False,
        created_at=NOW,
        metadata={},
    )


def test_risk_evaluation_request_wraps_order_intent_without_policy_behavior() -> None:
    request = RiskEvaluationRequest(
        request_id="risk-request-1",
        order_intent=make_order_intent(),
        requested_at=NOW,
        metadata={"policy_set": "interface-v0"},
    )

    assert request.order_intent.intent_id == "intent-1"
    assert request.metadata["policy_set"] == "interface-v0"
    assert not hasattr(request, "approve")
    assert not hasattr(request, "reject")
    assert not hasattr(request, "submit")
    assert not hasattr(request, "execute")

    with pytest.raises(TypeError):
        request.metadata["policy_set"] = "mutated"  # type: ignore[index]


def test_risk_evaluation_request_rejects_secret_or_exchange_payload_metadata() -> None:
    for forbidden_metadata in [
        {"raw_payload": "{}"},
        {"exchange_response": "ok"},
        {"account_id": "acct-1"},
        {"api_key": "not-a-real-key"},  # pragma: allowlist secret
    ]:
        with pytest.raises(ValueError, match="metadata must not contain exchange-specific"):
            RiskEvaluationRequest(
                request_id="risk-request-1",
                order_intent=make_order_intent(),
                requested_at=NOW,
                metadata=forbidden_metadata,
            )


def test_risk_evaluation_request_requires_stable_id_and_timestamp() -> None:
    with pytest.raises(ValueError, match="request_id must not be blank"):
        RiskEvaluationRequest(
            request_id="",
            order_intent=make_order_intent(),
            requested_at=NOW,
            metadata={},
        )

    with pytest.raises(ValueError, match="requested_at must be timezone-aware"):
        RiskEvaluationRequest(
            request_id="risk-request-1",
            order_intent=make_order_intent(),
            requested_at=datetime(2026, 5, 17, 12, 0),
            metadata={},
        )


def test_risk_evaluation_request_requires_order_intent_instance() -> None:
    with pytest.raises(ValueError, match="order_intent must be an OrderIntent"):
        RiskEvaluationRequest(
            request_id="risk-request-1",
            order_intent={"intent_id": "intent-1"},  # type: ignore[arg-type]
            requested_at=NOW,
            metadata={},
        )


def test_risk_engine_protocol_returns_existing_risk_decision_type() -> None:
    class ManualReviewRiskEngine:
        def evaluate(self, request: RiskEvaluationRequest) -> RiskDecision:
            return RiskDecision(
                decision_id="risk-decision-1",
                intent_id=request.order_intent.intent_id,
                status=RiskDecisionStatus.REQUIRES_REVIEW,
                reason="interface contract only",
                decided_at=NOW,
                metadata={"policy_set": "interface-v0"},
            )

    engine: RiskEngine = ManualReviewRiskEngine()
    decision = engine.evaluate(
        RiskEvaluationRequest(
            request_id="risk-request-1",
            order_intent=make_order_intent(),
            requested_at=NOW,
            metadata={},
        )
    )

    assert decision.status is RiskDecisionStatus.REQUIRES_REVIEW
    assert decision.intent_id == "intent-1"


def test_core_risk_interface_does_not_introduce_runtime_or_exchange_specific_terms() -> None:
    forbidden_terms = [
        "BingX",
        "REST",
        "WebSocket",
        "http",
        "database",
        "storage",
        "submit_order",
        "execute_order",
        "adapter",
        "live",
    ]

    scanned = {path: path.read_text(encoding="utf-8") for path in RISK_ROOT.rglob("*.py")}
    violations = [
        f"{path.relative_to(ROOT).as_posix()}:{term}"
        for path, content in scanned.items()
        for term in forbidden_terms
        if term.lower() in content.lower()
    ]

    assert violations == []
