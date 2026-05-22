"""Exchange-independent OMS order status transition policy."""

from collections.abc import Mapping
from types import MappingProxyType

from trading_system.core.domain import OrderStatus


class InvalidOrderStatusTransition(ValueError):
    """Raised when an OMS order status transition is not allowed."""


TERMINAL_ORDER_STATUSES: frozenset[OrderStatus] = frozenset(
    {
        OrderStatus.RISK_REJECTED,
        OrderStatus.FILLED,
        OrderStatus.CANCELED,
        OrderStatus.REJECTED,
        OrderStatus.EXPIRED,
        OrderStatus.UNKNOWN,
    }
)

OPERATOR_REVIEW_ORDER_STATUSES: frozenset[OrderStatus] = frozenset({OrderStatus.UNKNOWN})

ALLOWED_ORDER_STATUS_TRANSITIONS: Mapping[OrderStatus, frozenset[OrderStatus]] = MappingProxyType(
    {
        OrderStatus.CREATED: frozenset({OrderStatus.RISK_APPROVED}),
        OrderStatus.PENDING_RISK: frozenset(),
        OrderStatus.RISK_REJECTED: frozenset(),
        OrderStatus.RISK_APPROVED: frozenset({OrderStatus.ACCEPTED}),
        OrderStatus.ACCEPTED: frozenset({OrderStatus.SUBMITTED}),
        OrderStatus.SUBMITTED: frozenset(
            {
                OrderStatus.PARTIALLY_FILLED,
                OrderStatus.FILLED,
                OrderStatus.CANCELED,
                OrderStatus.REJECTED,
                OrderStatus.EXPIRED,
                OrderStatus.UNKNOWN,
            }
        ),
        OrderStatus.PARTIALLY_FILLED: frozenset(
            {
                OrderStatus.FILLED,
                OrderStatus.CANCELED,
                OrderStatus.EXPIRED,
                OrderStatus.UNKNOWN,
            }
        ),
        OrderStatus.FILLED: frozenset(),
        OrderStatus.CANCELED: frozenset(),
        OrderStatus.REJECTED: frozenset(),
        OrderStatus.EXPIRED: frozenset(),
        OrderStatus.UNKNOWN: frozenset(),
    }
)


def _normalize_order_status(status: OrderStatus | str) -> OrderStatus:
    return OrderStatus(status)


def is_terminal_order_status(status: OrderStatus | str) -> bool:
    return _normalize_order_status(status) in TERMINAL_ORDER_STATUSES


def allowed_next_order_statuses(status: OrderStatus | str) -> frozenset[OrderStatus]:
    return ALLOWED_ORDER_STATUS_TRANSITIONS[_normalize_order_status(status)]


def is_valid_order_status_transition(current: OrderStatus | str, target: OrderStatus | str) -> bool:
    try:
        current_status = _normalize_order_status(current)
        target_status = _normalize_order_status(target)
    except ValueError:
        return False

    return target_status in ALLOWED_ORDER_STATUS_TRANSITIONS[current_status]


def ensure_valid_order_status_transition(
    current: OrderStatus | str,
    target: OrderStatus | str,
) -> tuple[OrderStatus, OrderStatus]:
    current_status = _normalize_order_status(current)
    target_status = _normalize_order_status(target)

    if target_status not in ALLOWED_ORDER_STATUS_TRANSITIONS[current_status]:
        raise InvalidOrderStatusTransition(
            "order status transition "
            f"{current_status.value} -> {target_status.value} is not allowed"
        )

    return current_status, target_status
