from __future__ import annotations

from quant_system.config import RiskConfig
from quant_system.core.types import Signal


class RiskManager:
    def __init__(self, config: RiskConfig) -> None:
        self.config = config

    def check(
        self,
        signal: Signal,
        current_position: float,
        mark_price: float,
        realized_pnl: float,
    ) -> float:
        """Return approved order qty, 0 means reject."""
        if signal.side is None:
            return 0.0

        if realized_pnl <= -abs(self.config.max_daily_loss):
            return 0.0

        qty = min(self.config.max_order_size, max(0.1, signal.confidence / 2))
        if signal.side.value == "BUY":
            next_pos = current_position + qty
        else:
            next_pos = current_position - qty

        if abs(next_pos) > self.config.max_abs_position:
            return 0.0

        notional = qty * mark_price
        if notional <= 0:
            return 0.0

        return round(qty, 6)
