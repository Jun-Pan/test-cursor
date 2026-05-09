from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import UTC, datetime

from quant_system.core.types import MarketTick


@dataclass
class MockPriceCollector:
    symbol: str
    seed_price: float = 100.0
    drift: float = 0.0002
    volatility: float = 0.01

    def __post_init__(self) -> None:
        self._price = self.seed_price

    def collect_next(self) -> MarketTick:
        shock = random.gauss(mu=self.drift, sigma=self.volatility)
        self._price = max(0.1, self._price * (1 + shock))
        volume = max(0.01, random.lognormvariate(mu=-0.2, sigma=0.5))
        return MarketTick(
            symbol=self.symbol,
            ts=datetime.now(tz=UTC),
            price=round(self._price, 6),
            volume=round(volume, 6),
        )
