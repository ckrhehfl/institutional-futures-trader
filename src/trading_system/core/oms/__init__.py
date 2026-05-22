"""Exchange-independent OMS state machine helpers."""

from trading_system.core.oms.state_machine import (
    ALLOWED_ORDER_STATUS_TRANSITIONS,
    OPERATOR_REVIEW_ORDER_STATUSES,
    TERMINAL_ORDER_STATUSES,
    InvalidOrderStatusTransition,
    allowed_next_order_statuses,
    ensure_valid_order_status_transition,
    is_terminal_order_status,
    is_valid_order_status_transition,
)

__all__ = [
    "ALLOWED_ORDER_STATUS_TRANSITIONS",
    "OPERATOR_REVIEW_ORDER_STATUSES",
    "TERMINAL_ORDER_STATUSES",
    "InvalidOrderStatusTransition",
    "allowed_next_order_statuses",
    "ensure_valid_order_status_transition",
    "is_terminal_order_status",
    "is_valid_order_status_transition",
]
