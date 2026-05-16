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


def test_signal_allows_zero_valued_advisories() -> None:
    signal = Signal(
        signal_id="sig-neutral",
        symbol="BTC-USDT",
        created_at=NOW,
        source="example-strategy",
        confidence=Decimal("0"),
        regime="neutral",
        sizing_suggestion=Decimal("0"),
        metadata={"mode": "paper"},
    )

    assert signal.confidence == Decimal("0")
    assert signal.sizing_suggestion == Decimal("0")


def test_signal_allows_qualitative_confidence_labels() -> None:
    for confidence in ["low", "medium", "high"]:
        signal = Signal(
            signal_id=f"sig-{confidence}",
            symbol="BTC-USDT",
            created_at=NOW,
            source="example-strategy",
            confidence=confidence,
            regime="neutral",
            sizing_suggestion=Decimal("0"),
            metadata={"mode": "paper"},
        )

        assert signal.confidence == confidence


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

    raw_enum_intent = OrderIntent(
        intent_id="intent-raw",
        source_signal_id="sig-1",
        created_by="order_intent_builder",
        symbol="BTC-USDT",
        side=OrderSide.BUY.value,
        order_type=OrderType.MARKET.value,
        quantity=Decimal("0.001"),
        limit_price=None,
        time_in_force=TimeInForce.IOC.value,
        trading_mode=TradingMode.PAPER.value,
        execution_venue=ExecutionVenue.PAPER.value,
        leverage=Decimal("1"),
        reduce_only=False,
        close_only=False,
        post_only=False,
        created_at=NOW,
        metadata={},
    )
    assert raw_enum_intent.side is OrderSide.BUY
    assert raw_enum_intent.order_type is OrderType.MARKET
    assert raw_enum_intent.time_in_force is TimeInForce.IOC
    assert raw_enum_intent.trading_mode is TradingMode.PAPER
    assert raw_enum_intent.execution_venue is ExecutionVenue.PAPER


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


def test_order_intent_rejects_unknown_runtime_enum_values() -> None:
    valid_args = {
        "intent_id": "intent-1",
        "source_signal_id": "sig-1",
        "created_by": "order_intent_builder",
        "symbol": "BTC-USDT",
        "side": OrderSide.BUY,
        "order_type": OrderType.MARKET,
        "quantity": Decimal("0.001"),
        "limit_price": None,
        "time_in_force": TimeInForce.IOC,
        "trading_mode": TradingMode.PAPER,
        "execution_venue": ExecutionVenue.PAPER,
        "leverage": Decimal("1"),
        "reduce_only": False,
        "close_only": False,
        "post_only": False,
        "created_at": NOW,
        "metadata": {},
    }

    for field_name, invalid_value in [
        ("side", "bid"),
        ("order_type", "iceberg"),
        ("time_in_force", "maker_only"),
        ("trading_mode", "production"),
        ("execution_venue", "real_money"),
    ]:
        args = valid_args | {field_name: invalid_value}
        with pytest.raises(ValueError):
            OrderIntent(**args)


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


def test_market_order_intent_rejects_limit_price() -> None:
    with pytest.raises(ValueError, match="limit_price is only valid for limit orders"):
        OrderIntent(
            intent_id="intent-market-with-price",
            source_signal_id="sig-1",
            created_by="order_intent_builder",
            symbol="BTC-USDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("0.001"),
            limit_price=Decimal("100000"),
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


def test_market_order_intent_rejects_post_only_semantics() -> None:
    for time_in_force, post_only in [
        (TimeInForce.POST_ONLY, False),
        (TimeInForce.POST_ONLY.value, False),
        (TimeInForce.IOC, True),
    ]:
        with pytest.raises(ValueError, match="post-only is only valid for limit orders"):
            OrderIntent(
                intent_id=f"intent-market-{time_in_force}-{post_only}",
                source_signal_id="sig-1",
                created_by="order_intent_builder",
                symbol="BTC-USDT",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=Decimal("0.001"),
                limit_price=None,
                time_in_force=time_in_force,
                trading_mode=TradingMode.PAPER,
                execution_venue=ExecutionVenue.PAPER,
                leverage=Decimal("1"),
                reduce_only=False,
                close_only=False,
                post_only=post_only,
                created_at=NOW,
                metadata={},
            )


def test_limit_order_intent_rejects_immediate_post_only_semantics() -> None:
    for time_in_force in [TimeInForce.IOC, TimeInForce.FOK]:
        with pytest.raises(
            ValueError,
            match="post-only limit orders must use post-only time in force",
        ):
            OrderIntent(
                intent_id=f"intent-limit-post-only-{time_in_force.value}",
                source_signal_id="sig-1",
                created_by="order_intent_builder",
                symbol="BTC-USDT",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                quantity=Decimal("0.001"),
                limit_price=Decimal("100000"),
                time_in_force=time_in_force,
                trading_mode=TradingMode.PAPER,
                execution_venue=ExecutionVenue.PAPER,
                leverage=Decimal("1"),
                reduce_only=False,
                close_only=False,
                post_only=True,
                created_at=NOW,
                metadata={},
            )


def test_limit_order_intent_rejects_mismatched_post_only_fields() -> None:
    for time_in_force in [TimeInForce.POST_ONLY, TimeInForce.POST_ONLY.value]:
        with pytest.raises(ValueError, match="post-only fields must agree"):
            OrderIntent(
                intent_id=f"intent-limit-post-only-mismatch-{time_in_force}",
                source_signal_id="sig-1",
                created_by="order_intent_builder",
                symbol="BTC-USDT",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                quantity=Decimal("0.001"),
                limit_price=Decimal("100000"),
                time_in_force=time_in_force,
                trading_mode=TradingMode.PAPER,
                execution_venue=ExecutionVenue.PAPER,
                leverage=Decimal("1"),
                reduce_only=False,
                close_only=False,
                post_only=False,
                created_at=NOW,
                metadata={},
            )


def test_close_only_order_intent_requires_reduce_only() -> None:
    with pytest.raises(ValueError, match="close-only requires reduce-only"):
        OrderIntent(
            intent_id="intent-close-only",
            source_signal_id="sig-1",
            created_by="order_intent_builder",
            symbol="BTC-USDT",
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            quantity=Decimal("0.001"),
            limit_price=None,
            time_in_force=TimeInForce.IOC,
            trading_mode=TradingMode.PAPER,
            execution_venue=ExecutionVenue.PAPER,
            leverage=Decimal("1"),
            reduce_only=False,
            close_only=True,
            post_only=False,
            created_at=NOW,
            metadata={},
        )
