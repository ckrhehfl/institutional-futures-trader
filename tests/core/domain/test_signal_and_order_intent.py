from datetime import UTC, datetime
from decimal import Decimal

import pytest

from trading_system.core.domain import (
    ExecutionVenue,
    OrderIntent,
    OrderSide,
    OrderType,
    Signal,
    TimeInForce,
    TradingMode,
)

NOW = datetime(2026, 5, 15, 12, 0, tzinfo=UTC)


def test_signal_is_not_an_order_and_has_no_execution_fields() -> None:
    signal = Signal(
        signal_id="sig-1",
        symbol="BTC-USDT",
        created_at=NOW,
        source="example-strategy",
        confidence=Decimal("0.80"),
        regime="trend",
        sizing_suggestion=Decimal("0.10"),
        metadata={"mode": "paper"},
    )

    assert signal.symbol == "BTC-USDT"
    assert not hasattr(signal, "side")
    assert not hasattr(signal, "quantity")
    assert not hasattr(signal, "order_type")
    assert not hasattr(signal, "execute")


def test_order_intent_is_created_for_risk_review_not_execution() -> None:
    intent = OrderIntent(
        intent_id="intent-1",
        source_signal_id="sig-1",
        created_by="order_intent_builder",
        symbol="BTC-USDT",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("0.001"),
        limit_price=Decimal("100000"),
        time_in_force=TimeInForce.POST_ONLY,
        trading_mode=TradingMode.PAPER,
        execution_venue=ExecutionVenue.PAPER,
        leverage=Decimal("1"),
        reduce_only=False,
        close_only=False,
        post_only=True,
        created_at=NOW,
        metadata={"reason": "test"},
    )

    assert intent.trading_mode is TradingMode.PAPER
    assert intent.execution_venue is ExecutionVenue.PAPER
    assert not hasattr(intent, "submit")
    assert not hasattr(intent, "execute")


def test_order_intent_rejects_strategy_or_ai_creator() -> None:
    for created_by in ["strategy", "ai", "ml"]:
        with pytest.raises(ValueError, match="OrderIntent creator must be"):
            OrderIntent(
                intent_id="intent-1",
                source_signal_id="sig-1",
                created_by=created_by,
                symbol="BTC-USDT",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=Decimal("0.001"),
                limit_price=None,
                time_in_force=TimeInForce.IOC,
                trading_mode=TradingMode.PAPER,
                execution_venue=ExecutionVenue.PAPER,
                leverage=Decimal("1"),
                reduce_only=False,
                close_only=False,
                post_only=False,
                created_at=NOW,
                metadata={},
            )


def test_priced_order_intent_requires_limit_price() -> None:
    with pytest.raises(ValueError, match="limit_price is required"):
        OrderIntent(
            intent_id="intent-limit",
            source_signal_id="sig-1",
            created_by="order_intent_builder",
            symbol="BTC-USDT",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("0.001"),
            limit_price=None,
            time_in_force=TimeInForce.GTC,
            trading_mode=TradingMode.PAPER,
            execution_venue=ExecutionVenue.PAPER,
            leverage=Decimal("1"),
            reduce_only=False,
            close_only=False,
            post_only=False,
            created_at=NOW,
            metadata={},
        )


def test_stop_order_intents_are_rejected_until_trigger_price_exists() -> None:
    for order_type in [OrderType.STOP, OrderType.STOP_LIMIT]:
        with pytest.raises(ValueError, match="stop order types are not supported"):
            OrderIntent(
                intent_id=f"intent-{order_type.value}",
                source_signal_id="sig-1",
                created_by="order_intent_builder",
                symbol="BTC-USDT",
                side=OrderSide.BUY,
                order_type=order_type,
                quantity=Decimal("0.001"),
                limit_price=Decimal("100000"),
                time_in_force=TimeInForce.GTC,
                trading_mode=TradingMode.PAPER,
                execution_venue=ExecutionVenue.PAPER,
                leverage=Decimal("1"),
                reduce_only=False,
                close_only=False,
                post_only=False,
                created_at=NOW,
                metadata={},
            )
