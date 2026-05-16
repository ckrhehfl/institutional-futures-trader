from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from trading_system.core.domain import (
    Fee,
    Fill,
    FundingFee,
    MarginMode,
    Order,
    OrderSide,
    OrderStatus,
    OrderType,
    PnL,
    Position,
    PositionMode,
    PositionSide,
    TimeInForce,
)

NOW = datetime(2026, 5, 15, 12, 0, tzinfo=UTC)


def test_order_and_fill_validate_positive_values() -> None:
    order = Order(
        order_id="order-1",
        intent_id="intent-1",
        symbol="BTC-USDT",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        status=OrderStatus.ACCEPTED,
        quantity=Decimal("0.001"),
        filled_quantity=Decimal("0"),
        limit_price=Decimal("100000"),
        time_in_force=TimeInForce.POST_ONLY,
        reduce_only=False,
        close_only=False,
        post_only=True,
        created_at=NOW,
        updated_at=NOW,
        metadata={},
    )
    assert order.remaining_quantity == Decimal("0.001")

    with pytest.raises(ValueError, match="quantity must be positive"):
        replace(order, quantity=Decimal("0"))

    fill = Fill(
        fill_id="fill-1",
        order_id="order-1",
        symbol="BTC-USDT",
        side=OrderSide.BUY,
        quantity=Decimal("0.001"),
        price=Decimal("100000"),
        fee=Decimal("0.10"),
        filled_at=NOW,
        metadata={},
    )
    assert fill.notional == Decimal("100.000")


def test_pre_execution_order_states_reject_filled_quantity() -> None:
    for status in [
        OrderStatus.CREATED,
        OrderStatus.PENDING_RISK,
        OrderStatus.RISK_REJECTED,
        OrderStatus.RISK_APPROVED,
        OrderStatus.ACCEPTED,
    ]:
        with pytest.raises(ValueError, match="pre-execution order states must have zero fills"):
            Order(
                order_id=f"order-{status.value}",
                intent_id="intent-1",
                symbol="BTC-USDT",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                status=status,
                quantity=Decimal("0.001"),
                filled_quantity=Decimal("0.0005"),
                limit_price=Decimal("100000"),
                time_in_force=TimeInForce.GTC,
                reduce_only=False,
                close_only=False,
                post_only=False,
                created_at=NOW,
                updated_at=NOW,
                metadata={},
            )


def test_order_rejects_missing_limit_price_for_priced_orders() -> None:
    order = Order(
        order_id="order-1",
        intent_id="intent-1",
        symbol="BTC-USDT",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        status=OrderStatus.ACCEPTED,
        quantity=Decimal("0.001"),
        filled_quantity=Decimal("0"),
        limit_price=Decimal("100000"),
        time_in_force=TimeInForce.POST_ONLY,
        reduce_only=False,
        close_only=False,
        post_only=True,
        created_at=NOW,
        updated_at=NOW,
        metadata={},
    )

    with pytest.raises(ValueError, match="limit_price is required"):
        replace(order, limit_price=None)


def test_order_rejects_unknown_runtime_enum_values() -> None:
    valid_args = {
        "order_id": "order-1",
        "intent_id": "intent-1",
        "symbol": "BTC-USDT",
        "side": OrderSide.BUY,
        "order_type": OrderType.MARKET,
        "status": OrderStatus.SUBMITTED,
        "quantity": Decimal("0.001"),
        "filled_quantity": Decimal("0"),
        "limit_price": None,
        "time_in_force": TimeInForce.IOC,
        "reduce_only": False,
        "close_only": False,
        "post_only": False,
        "created_at": NOW,
        "updated_at": NOW,
        "metadata": {},
    }

    for field_name, invalid_value in [
        ("side", "bid"),
        ("order_type", "iceberg"),
        ("status", "partly_done"),
        ("time_in_force", "maker_only"),
    ]:
        args = valid_args | {field_name: invalid_value}
        with pytest.raises(ValueError):
            Order(**args)


def test_market_order_rejects_limit_price() -> None:
    with pytest.raises(ValueError, match="limit_price is only valid for limit orders"):
        Order(
            order_id="order-market-with-price",
            intent_id="intent-1",
            symbol="BTC-USDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            status=OrderStatus.ACCEPTED,
            quantity=Decimal("0.001"),
            filled_quantity=Decimal("0"),
            limit_price=Decimal("100000"),
            time_in_force=TimeInForce.IOC,
            reduce_only=False,
            close_only=False,
            post_only=False,
            created_at=NOW,
            updated_at=NOW,
            metadata={},
        )


def test_order_rejects_stop_types_until_trigger_price_exists() -> None:
    for order_type in [OrderType.STOP, OrderType.STOP_LIMIT]:
        with pytest.raises(ValueError, match="stop order types are not supported"):
            Order(
                order_id=f"order-{order_type.value}",
                intent_id="intent-1",
                symbol="BTC-USDT",
                side=OrderSide.BUY,
                order_type=order_type,
                status=OrderStatus.ACCEPTED,
                quantity=Decimal("0.001"),
                filled_quantity=Decimal("0"),
                limit_price=Decimal("100000"),
                time_in_force=TimeInForce.GTC,
                reduce_only=False,
                close_only=False,
                post_only=False,
                created_at=NOW,
                updated_at=NOW,
                metadata={},
            )


def test_market_order_rejects_post_only_semantics() -> None:
    for time_in_force, post_only in [
        (TimeInForce.POST_ONLY, False),
        (TimeInForce.POST_ONLY.value, False),
        (TimeInForce.IOC, True),
    ]:
        with pytest.raises(ValueError, match="post-only is only valid for limit orders"):
            Order(
                order_id=f"order-market-{time_in_force}-{post_only}",
                intent_id="intent-1",
                symbol="BTC-USDT",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                status=OrderStatus.ACCEPTED,
                quantity=Decimal("0.001"),
                filled_quantity=Decimal("0"),
                limit_price=None,
                time_in_force=time_in_force,
                reduce_only=False,
                close_only=False,
                post_only=post_only,
                created_at=NOW,
                updated_at=NOW,
                metadata={},
            )


def test_limit_order_rejects_immediate_post_only_semantics() -> None:
    for time_in_force in [TimeInForce.IOC, TimeInForce.FOK]:
        with pytest.raises(
            ValueError,
            match="post-only limit orders must use post-only time in force",
        ):
            Order(
                order_id=f"order-limit-post-only-{time_in_force.value}",
                intent_id="intent-1",
                symbol="BTC-USDT",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                status=OrderStatus.ACCEPTED,
                quantity=Decimal("0.001"),
                filled_quantity=Decimal("0"),
                limit_price=Decimal("100000"),
                time_in_force=time_in_force,
                reduce_only=False,
                close_only=False,
                post_only=True,
                created_at=NOW,
                updated_at=NOW,
                metadata={},
            )


def test_limit_order_rejects_mismatched_post_only_fields() -> None:
    for time_in_force in [TimeInForce.POST_ONLY, TimeInForce.POST_ONLY.value]:
        with pytest.raises(ValueError, match="post-only fields must agree"):
            Order(
                order_id=f"order-limit-post-only-mismatch-{time_in_force}",
                intent_id="intent-1",
                symbol="BTC-USDT",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                status=OrderStatus.ACCEPTED,
                quantity=Decimal("0.001"),
                filled_quantity=Decimal("0"),
                limit_price=Decimal("100000"),
                time_in_force=time_in_force,
                reduce_only=False,
                close_only=False,
                post_only=False,
                created_at=NOW,
                updated_at=NOW,
                metadata={},
            )


def test_filled_order_must_have_no_remaining_quantity() -> None:
    order = Order(
        order_id="order-1",
        intent_id="intent-1",
        symbol="BTC-USDT",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        status=OrderStatus.FILLED,
        quantity=Decimal("0.001"),
        filled_quantity=Decimal("0.001"),
        limit_price=Decimal("100000"),
        time_in_force=TimeInForce.GTC,
        reduce_only=False,
        close_only=False,
        post_only=False,
        created_at=NOW,
        updated_at=NOW,
        metadata={},
    )

    assert order.remaining_quantity == Decimal("0.000")

    with pytest.raises(ValueError, match="filled order must have no remaining quantity"):
        replace(order, filled_quantity=Decimal("0.0005"))


def test_complete_fills_require_filled_status() -> None:
    for status in [OrderStatus.CANCELED, OrderStatus.REJECTED, OrderStatus.EXPIRED]:
        with pytest.raises(ValueError, match="complete filled quantity requires filled status"):
            Order(
                order_id=f"order-{status.value}",
                intent_id="intent-1",
                symbol="BTC-USDT",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                status=status,
                quantity=Decimal("0.001"),
                filled_quantity=Decimal("0.001"),
                limit_price=Decimal("100000"),
                time_in_force=TimeInForce.GTC,
                reduce_only=False,
                close_only=False,
                post_only=False,
                created_at=NOW,
                updated_at=NOW,
                metadata={},
            )


def test_partially_filled_order_requires_partial_quantity() -> None:
    order = Order(
        order_id="order-1",
        intent_id="intent-1",
        symbol="BTC-USDT",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        status=OrderStatus.PARTIALLY_FILLED,
        quantity=Decimal("0.001"),
        filled_quantity=Decimal("0.0005"),
        limit_price=Decimal("100000"),
        time_in_force=TimeInForce.GTC,
        reduce_only=False,
        close_only=False,
        post_only=False,
        created_at=NOW,
        updated_at=NOW,
        metadata={},
    )

    assert order.remaining_quantity == Decimal("0.0005")

    for filled_quantity in [Decimal("0"), Decimal("0.001")]:
        with pytest.raises(ValueError, match="partially filled order requires"):
            replace(order, filled_quantity=filled_quantity)

    for filled_quantity in [Decimal("0"), Decimal("0.001")]:
        with pytest.raises(ValueError, match="partially filled order requires"):
            replace(
                order,
                status=OrderStatus.PARTIALLY_FILLED.value,
                filled_quantity=filled_quantity,
            )

    raw_status_order = replace(
        order,
        status=OrderStatus.PARTIALLY_FILLED.value,
        filled_quantity=Decimal("0.0005"),
    )
    assert raw_status_order.status is OrderStatus.PARTIALLY_FILLED


def test_partial_fills_require_partial_fill_status() -> None:
    for status in [
        OrderStatus.SUBMITTED,
        OrderStatus.CANCELED,
        OrderStatus.REJECTED,
        OrderStatus.EXPIRED,
        OrderStatus.UNKNOWN,
    ]:
        with pytest.raises(ValueError, match="partial filled quantity requires partial status"):
            Order(
                order_id=f"order-{status.value}",
                intent_id="intent-1",
                symbol="BTC-USDT",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                status=status,
                quantity=Decimal("0.001"),
                filled_quantity=Decimal("0.0005"),
                limit_price=Decimal("100000"),
                time_in_force=TimeInForce.GTC,
                reduce_only=False,
                close_only=False,
                post_only=False,
                created_at=NOW,
                updated_at=NOW,
                metadata={},
            )


def test_order_updated_at_must_not_predate_created_at() -> None:
    with pytest.raises(ValueError, match="updated_at must not predate created_at"):
        Order(
            order_id="order-1",
            intent_id="intent-1",
            symbol="BTC-USDT",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            status=OrderStatus.ACCEPTED,
            quantity=Decimal("0.001"),
            filled_quantity=Decimal("0"),
            limit_price=Decimal("100000"),
            time_in_force=TimeInForce.GTC,
            reduce_only=False,
            close_only=False,
            post_only=False,
            created_at=NOW,
            updated_at=datetime(2026, 5, 15, 11, 59, tzinfo=UTC),
            metadata={},
        )


def test_non_flat_position_requires_positive_quantity() -> None:
    for side in [PositionSide.LONG, PositionSide.SHORT]:
        with pytest.raises(ValueError, match="non-flat position quantity must be positive"):
            Position(
                symbol="BTC-USDT",
                side=side,
                quantity=Decimal("0"),
                entry_price=Decimal("100000"),
                mark_price=Decimal("101000"),
                leverage=Decimal("1"),
                margin_mode=MarginMode.ISOLATED,
                position_mode=PositionMode.ONE_WAY,
                maintenance_margin=Decimal("0"),
                liquidation_price=None,
                updated_at=NOW,
                metadata={},
            )


def test_position_rejects_unknown_runtime_enum_values() -> None:
    valid_args = {
        "symbol": "BTC-USDT",
        "side": PositionSide.LONG,
        "quantity": Decimal("0.001"),
        "entry_price": Decimal("100000"),
        "mark_price": Decimal("101000"),
        "leverage": Decimal("1"),
        "margin_mode": MarginMode.ISOLATED,
        "position_mode": PositionMode.ONE_WAY,
        "maintenance_margin": Decimal("0"),
        "liquidation_price": None,
        "updated_at": NOW,
        "metadata": {},
    }

    for field_name, invalid_value in [
        ("side", "sideways"),
        ("margin_mode", "portfolio"),
        ("position_mode", "bad"),
    ]:
        args = valid_args | {field_name: invalid_value}
        with pytest.raises(ValueError):
            Position(**args)


def test_raw_flat_position_side_follows_flat_validation() -> None:
    flat_position = Position(
        symbol="BTC-USDT",
        side=PositionSide.FLAT.value,
        quantity=Decimal("0"),
        entry_price=None,
        mark_price=Decimal("101000"),
        leverage=Decimal("1"),
        margin_mode=MarginMode.ISOLATED,
        position_mode=PositionMode.ONE_WAY,
        maintenance_margin=Decimal("0"),
        liquidation_price=None,
        updated_at=NOW,
        metadata={},
    )
    assert flat_position.side is PositionSide.FLAT

    with pytest.raises(ValueError, match="flat position quantity must be zero"):
        Position(
            symbol="BTC-USDT",
            side=PositionSide.FLAT.value,
            quantity=Decimal("0.001"),
            entry_price=None,
            mark_price=Decimal("101000"),
            leverage=Decimal("1"),
            margin_mode=MarginMode.ISOLATED,
            position_mode=PositionMode.ONE_WAY,
            maintenance_margin=Decimal("0"),
            liquidation_price=None,
            updated_at=NOW,
            metadata={},
        )


def test_fee_funding_pnl_and_position_validate_decimal_values() -> None:
    fee = Fee(symbol="BTC-USDT", amount=Decimal("0.10"), asset="USDT", occurred_at=NOW, metadata={})
    funding = FundingFee(
        symbol="BTC-USDT",
        amount=Decimal("-0.05"),
        asset="USDT",
        funding_timestamp=NOW,
        occurred_at=NOW,
        metadata={},
    )
    pnl = PnL(
        symbol="BTC-USDT",
        realized=Decimal("1.20"),
        unrealized=Decimal("0.50"),
        fees=Decimal("0.10"),
        funding=Decimal("-0.05"),
        updated_at=NOW,
        metadata={},
    )
    position = Position(
        symbol="BTC-USDT",
        side=PositionSide.LONG,
        quantity=Decimal("0.001"),
        entry_price=Decimal("100000"),
        mark_price=Decimal("101000"),
        leverage=Decimal("1"),
        margin_mode=MarginMode.ISOLATED,
        position_mode=PositionMode.ONE_WAY,
        maintenance_margin=Decimal("5"),
        liquidation_price=None,
        updated_at=NOW,
        metadata={},
    )

    assert fee.amount == Decimal("0.10")
    assert funding.funding_timestamp == NOW
    assert pnl.unrealized == Decimal("0.50")
    assert position.maintenance_margin == Decimal("5")


def test_funding_fee_rejects_non_finite_amount() -> None:
    for amount in [Decimal("Infinity"), Decimal("-Infinity"), Decimal("NaN")]:
        with pytest.raises(ValueError, match="amount must be finite"):
            FundingFee(
                symbol="BTC-USDT",
                amount=amount,
                asset="USDT",
                funding_timestamp=NOW,
                occurred_at=NOW,
                metadata={},
            )


def test_pnl_rejects_non_finite_signed_values() -> None:
    pnl = PnL(
        symbol="BTC-USDT",
        realized=Decimal("1.20"),
        unrealized=Decimal("-0.50"),
        fees=Decimal("0.10"),
        funding=Decimal("-0.05"),
        updated_at=NOW,
        metadata={},
    )

    for field_name in ["realized", "unrealized", "funding"]:
        for value in [Decimal("Infinity"), Decimal("-Infinity"), Decimal("NaN")]:
            with pytest.raises(ValueError, match=f"{field_name} must be finite"):
                replace(pnl, **{field_name: value})


def test_flat_position_can_represent_zero_exposure() -> None:
    flat_without_entry = Position(
        symbol="BTC-USDT",
        side=PositionSide.FLAT,
        quantity=Decimal("0"),
        entry_price=None,
        mark_price=Decimal("101000"),
        leverage=Decimal("1"),
        margin_mode=MarginMode.ISOLATED,
        position_mode=PositionMode.ONE_WAY,
        maintenance_margin=Decimal("0"),
        liquidation_price=None,
        updated_at=NOW,
        metadata={},
    )
    flat_with_zero_entry = replace(flat_without_entry, entry_price=Decimal("0"))

    assert flat_without_entry.entry_price is None
    assert flat_with_zero_entry.entry_price == Decimal("0")

    with pytest.raises(ValueError, match="flat position quantity must be zero"):
        replace(flat_without_entry, quantity=Decimal("0.001"))

    with pytest.raises(ValueError, match="flat position maintenance_margin must be zero"):
        replace(flat_without_entry, maintenance_margin=Decimal("5"))

    with pytest.raises(ValueError, match="flat position liquidation_price must be absent"):
        replace(flat_without_entry, liquidation_price=Decimal("90000"))
