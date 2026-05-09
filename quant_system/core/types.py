from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True)
class MarketTick:
    symbol: str
    ts: datetime
    price: float
    volume: float


@dataclass(frozen=True)
class Signal:
    symbol: str
    ts: datetime
    side: Side | None
    confidence: float
    reason: str


@dataclass(frozen=True)
class Order:
    symbol: str
    ts: datetime
    side: Side
    qty: float
    price: float


@dataclass(frozen=True)
class Fill:
    symbol: str
    ts: datetime
    side: Side
    qty: float
    price: float
