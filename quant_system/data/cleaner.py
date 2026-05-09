from __future__ import annotations

from quant_system.core.types import MarketTick


class TickCleaner:
    """Normalize and validate market ticks."""

    def clean(self, tick: MarketTick) -> MarketTick | None:
        if tick.price <= 0 or tick.volume <= 0:
            return None
        return MarketTick(
            symbol=tick.symbol.strip().upper(),
            ts=tick.ts,
            price=float(tick.price),
            volume=float(tick.volume),
        )
