from trading_system.core.domain import (
    ExecutionVenue,
    MarginMode,
    OrderSide,
    OrderStatus,
    OrderType,
    PositionMode,
    PositionSide,
    TimeInForce,
    TradingMode,
)


def test_domain_enums_use_exchange_neutral_values() -> None:
    assert TradingMode.PAPER.value == "paper"
    assert ExecutionVenue.LIVE.value == "live"
    assert OrderSide.BUY.value == "buy"
    assert OrderType.LIMIT.value == "limit"
    assert TimeInForce.POST_ONLY.value == "post_only"
    assert OrderStatus.CANCELED.value == "canceled"
    assert PositionSide.FLAT.value == "flat"
    assert MarginMode.ISOLATED.value == "isolated"
    assert PositionMode.HEDGE.value == "hedge"
