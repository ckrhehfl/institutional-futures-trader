import pytest

from trading_system.core.domain import OrderStatus
from trading_system.core.oms import (
    ALLOWED_ORDER_STATUS_TRANSITIONS,
    OPERATOR_REVIEW_ORDER_STATUSES,
    TERMINAL_ORDER_STATUSES,
    InvalidOrderStatusTransition,
    allowed_next_order_statuses,
    ensure_valid_order_status_transition,
    is_terminal_order_status,
    is_valid_order_status_transition,
)

ALLOWED_TRANSITIONS = frozenset(
    {
        (OrderStatus.CREATED, OrderStatus.RISK_APPROVED),
        (OrderStatus.RISK_APPROVED, OrderStatus.ACCEPTED),
        (OrderStatus.ACCEPTED, OrderStatus.SUBMITTED),
        (OrderStatus.SUBMITTED, OrderStatus.PARTIALLY_FILLED),
        (OrderStatus.SUBMITTED, OrderStatus.FILLED),
        (OrderStatus.SUBMITTED, OrderStatus.CANCELED),
        (OrderStatus.SUBMITTED, OrderStatus.REJECTED),
        (OrderStatus.SUBMITTED, OrderStatus.EXPIRED),
        (OrderStatus.SUBMITTED, OrderStatus.UNKNOWN),
        (OrderStatus.PARTIALLY_FILLED, OrderStatus.FILLED),
        (OrderStatus.PARTIALLY_FILLED, OrderStatus.CANCELED),
        (OrderStatus.PARTIALLY_FILLED, OrderStatus.EXPIRED),
        (OrderStatus.PARTIALLY_FILLED, OrderStatus.UNKNOWN),
    }
)

TERMINAL_STATUSES = frozenset(
    {
        OrderStatus.RISK_REJECTED,
        OrderStatus.FILLED,
        OrderStatus.CANCELED,
        OrderStatus.REJECTED,
        OrderStatus.EXPIRED,
        OrderStatus.UNKNOWN,
    }
)


def test_all_allowed_transitions_are_valid() -> None:
    assert ALLOWED_ORDER_STATUS_TRANSITIONS == {
        status: frozenset(target for current, target in ALLOWED_TRANSITIONS if current == status)
        for status in OrderStatus
    }

    for current, target in ALLOWED_TRANSITIONS:
        assert is_valid_order_status_transition(current, target)


def test_ensure_valid_order_status_transition_returns_normalized_tuple() -> None:
    assert ensure_valid_order_status_transition(
        OrderStatus.ACCEPTED,
        OrderStatus.SUBMITTED,
    ) == (OrderStatus.ACCEPTED, OrderStatus.SUBMITTED)


def test_raw_enum_strings_are_normalized() -> None:
    assert ensure_valid_order_status_transition("created", "risk_approved") == (
        OrderStatus.CREATED,
        OrderStatus.RISK_APPROVED,
    )
    assert is_terminal_order_status("filled")
    assert (
        allowed_next_order_statuses("submitted")
        == ALLOWED_ORDER_STATUS_TRANSITIONS[OrderStatus.SUBMITTED]
    )


def test_invalid_enum_strings_fail_closed() -> None:
    with pytest.raises(ValueError):
        ensure_valid_order_status_transition("not_a_status", OrderStatus.CREATED)

    assert not is_valid_order_status_transition("not_a_status", OrderStatus.CREATED)


def test_created_to_submitted_is_forbidden() -> None:
    assert not is_valid_order_status_transition(OrderStatus.CREATED, OrderStatus.SUBMITTED)


def test_created_to_risk_approved_is_valid() -> None:
    assert is_valid_order_status_transition(OrderStatus.CREATED, OrderStatus.RISK_APPROVED)


def test_created_to_pending_risk_is_forbidden() -> None:
    assert not is_valid_order_status_transition(OrderStatus.CREATED, OrderStatus.PENDING_RISK)


def test_pending_risk_to_risk_approved_is_forbidden() -> None:
    assert not is_valid_order_status_transition(OrderStatus.PENDING_RISK, OrderStatus.RISK_APPROVED)


def test_pending_risk_to_risk_rejected_is_forbidden() -> None:
    assert not is_valid_order_status_transition(OrderStatus.PENDING_RISK, OrderStatus.RISK_REJECTED)


def test_pending_risk_to_submitted_is_forbidden() -> None:
    assert not is_valid_order_status_transition(OrderStatus.PENDING_RISK, OrderStatus.SUBMITTED)


def test_pending_risk_has_no_valid_outbound_transitions() -> None:
    for target in OrderStatus:
        assert not is_valid_order_status_transition(OrderStatus.PENDING_RISK, target)


def test_risk_rejected_has_no_valid_outbound_transitions() -> None:
    for target in OrderStatus:
        assert not is_valid_order_status_transition(OrderStatus.RISK_REJECTED, target)


@pytest.mark.parametrize("target", [OrderStatus.PENDING_RISK, OrderStatus.RISK_REJECTED])
def test_no_status_can_transition_into_pre_order_or_risk_rejected_statuses(
    target: OrderStatus,
) -> None:
    for current in OrderStatus:
        assert not is_valid_order_status_transition(current, target)


@pytest.mark.parametrize(
    "terminal_status", sorted(TERMINAL_STATUSES, key=lambda status: status.value)
)
def test_terminal_states_have_no_valid_outbound_transitions(terminal_status: OrderStatus) -> None:
    for target in OrderStatus:
        assert not is_valid_order_status_transition(terminal_status, target)


def test_unknown_target_is_only_allowed_after_submission_started() -> None:
    allowed_sources = {OrderStatus.SUBMITTED, OrderStatus.PARTIALLY_FILLED}

    for current in OrderStatus:
        assert is_valid_order_status_transition(current, OrderStatus.UNKNOWN) == (
            current in allowed_sources
        )


def test_partially_filled_to_rejected_is_forbidden_in_v0() -> None:
    assert not is_valid_order_status_transition(OrderStatus.PARTIALLY_FILLED, OrderStatus.REJECTED)


def test_allowed_next_order_statuses_returns_frozenset() -> None:
    assert isinstance(allowed_next_order_statuses(OrderStatus.SUBMITTED), frozenset)


def test_every_order_status_is_represented_in_transition_table() -> None:
    assert set(ALLOWED_ORDER_STATUS_TRANSITIONS) == set(OrderStatus)


def test_transition_table_cannot_be_mutated_at_runtime() -> None:
    with pytest.raises(TypeError):
        ALLOWED_ORDER_STATUS_TRANSITIONS[OrderStatus.CREATED] = frozenset()


def test_terminal_status_helper_matches_policy() -> None:
    assert TERMINAL_ORDER_STATUSES == TERMINAL_STATUSES
    assert OPERATOR_REVIEW_ORDER_STATUSES == frozenset({OrderStatus.UNKNOWN})

    for status in OrderStatus:
        assert is_terminal_order_status(status) == (status in TERMINAL_STATUSES)


def test_is_valid_transition_returns_false_without_raising_for_invalid_transition() -> None:
    assert not is_valid_order_status_transition(OrderStatus.CREATED, OrderStatus.FILLED)


def test_ensure_valid_transition_raises_domain_exception_for_invalid_transition() -> None:
    with pytest.raises(InvalidOrderStatusTransition):
        ensure_valid_order_status_transition(OrderStatus.CREATED, OrderStatus.FILLED)
