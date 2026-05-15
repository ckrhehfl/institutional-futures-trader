"""Exchange-neutral domain enumerations."""

from enum import StrEnum


class TradingMode(StrEnum):
    BACKTEST = "backtest"
    PAPER = "paper"
    DEMO = "demo"
    LIVE = "live"


class ExecutionVenue(StrEnum):
    BACKTEST = "backtest"
    PAPER = "paper"
    DEMO = "demo"
    LIVE = "live"


class OrderSide(StrEnum):
    BUY = "buy"
    SELL = "sell"


class OrderType(StrEnum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class TimeInForce(StrEnum):
    GTC = "gtc"
    IOC = "ioc"
    FOK = "fok"
    POST_ONLY = "post_only"


class OrderStatus(StrEnum):
    CREATED = "created"
    PENDING_RISK = "pending_risk"
    RISK_REJECTED = "risk_rejected"
    RISK_APPROVED = "risk_approved"
    ACCEPTED = "accepted"
    SUBMITTED = "submitted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELED = "canceled"
    REJECTED = "rejected"
    EXPIRED = "expired"
    UNKNOWN = "unknown"


class PositionSide(StrEnum):
    LONG = "long"
    SHORT = "short"
    FLAT = "flat"


class MarginMode(StrEnum):
    ISOLATED = "isolated"
    CROSS = "cross"


class PositionMode(StrEnum):
    ONE_WAY = "one_way"
    HEDGE = "hedge"


class RiskDecisionStatus(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"


class ReconciliationStatus(StrEnum):
    MATCHED = "matched"
    DRIFT_DETECTED = "drift_detected"
    UNCERTAIN = "uncertain"
    REQUIRES_REVIEW = "requires_review"
