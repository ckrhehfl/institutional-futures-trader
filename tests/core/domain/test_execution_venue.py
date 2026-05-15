from datetime import UTC, datetime
from decimal import Decimal

import pytest

from trading_system.core.domain import (
    ExecutionVenue,
    OrderIntent,
    OrderSide,
    OrderType,
    TimeInForce,
    TradingMode,
)

NOW = datetime(2026, 5, 15, 12, 0, tzinfo=UTC)


def make_intent(mode: TradingMode, venue: ExecutionVenue) -> OrderIntent:
    return OrderIntent(
        intent_id="intent-1",
        source_signal_id="sig-1",
        created_by="order_intent_builder",
        symbol="BTC-USDT",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=Decimal("0.001"),
        limit_price=None,
        time_in_force=TimeInForce.IOC,
        trading_mode=mode,
        execution_venue=venue,
        leverage=Decimal("1"),
        reduce_only=False,
        close_only=False,
        post_only=False,
        created_at=NOW,
        metadata={},
    )


def test_paper_demo_backtest_venues_are_separate() -> None:
    assert (
        make_intent(TradingMode.BACKTEST, ExecutionVenue.BACKTEST).execution_venue
        is ExecutionVenue.BACKTEST
    )
    assert (
        make_intent(TradingMode.PAPER, ExecutionVenue.PAPER).execution_venue
        is ExecutionVenue.PAPER
    )
    assert make_intent(TradingMode.DEMO, ExecutionVenue.DEMO).execution_venue is ExecutionVenue.DEMO

    with pytest.raises(ValueError, match="paper mode must use paper execution venue"):
        make_intent(TradingMode.PAPER, ExecutionVenue.LIVE)

    with pytest.raises(ValueError, match="demo mode must use demo execution venue"):
        make_intent(TradingMode.DEMO, ExecutionVenue.LIVE)

    with pytest.raises(ValueError, match="live mode is not supported by domain v0"):
        make_intent(TradingMode.LIVE, ExecutionVenue.LIVE)


def test_raw_config_mode_and_venue_values_follow_same_boundary() -> None:
    intent = make_intent(TradingMode.PAPER.value, ExecutionVenue.PAPER.value)
    assert intent.trading_mode == TradingMode.PAPER
    assert intent.execution_venue == ExecutionVenue.PAPER

    with pytest.raises(ValueError, match="live mode is not supported by domain v0"):
        make_intent(TradingMode.LIVE.value, ExecutionVenue.LIVE.value)

    with pytest.raises(ValueError, match="paper mode must use paper execution venue"):
        make_intent(TradingMode.PAPER.value, ExecutionVenue.LIVE.value)
