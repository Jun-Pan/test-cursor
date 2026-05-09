from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from quant_system.config import ExecutionConfig
from quant_system.core.types import Fill, Order, Side


@dataclass
class PortfolioState:
    cash: float
    position: float = 0.0
    avg_entry: float = 0.0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0

    def mark_to_market(self, mark_price: float) -> None:
        if self.position == 0:
            self.unrealized_pnl = 0.0
            return
        self.unrealized_pnl = (mark_price - self.avg_entry) * self.position

    @property
    def equity(self) -> float:
        return self.cash + self.unrealized_pnl


class SimulatedExecutionEngine:
    def __init__(self, config: ExecutionConfig) -> None:
        self.state = PortfolioState(cash=config.starting_cash)

    def place_and_fill(self, symbol: str, ts: datetime, side: Side, qty: float, price: float) -> tuple[Order, Fill]:
        order = Order(symbol=symbol, ts=ts, side=side, qty=qty, price=price)
        fill = Fill(symbol=symbol, ts=ts, side=side, qty=qty, price=price)
        self._apply_fill(fill)
        return order, fill

    def _apply_fill(self, fill: Fill) -> None:
        signed_qty = fill.qty if fill.side == Side.BUY else -fill.qty
        prior_pos = self.state.position
        new_pos = prior_pos + signed_qty

        if prior_pos == 0 or (prior_pos > 0 and signed_qty > 0) or (prior_pos < 0 and signed_qty < 0):
            # Same direction: update weighted average entry.
            total_qty = abs(prior_pos) + abs(signed_qty)
            weighted_price = (
                (abs(prior_pos) * self.state.avg_entry) + (abs(signed_qty) * fill.price)
            ) / total_qty
            self.state.avg_entry = weighted_price
        else:
            # Opposite direction: realize pnl on closed quantity.
            closed_qty = min(abs(prior_pos), abs(signed_qty))
            direction = 1 if prior_pos > 0 else -1
            pnl = (fill.price - self.state.avg_entry) * closed_qty * direction
            self.state.realized_pnl += pnl

            # If position flips direction, new average is current fill price.
            if prior_pos != 0 and (prior_pos > 0 > new_pos or prior_pos < 0 < new_pos):
                self.state.avg_entry = fill.price
            elif new_pos == 0:
                self.state.avg_entry = 0.0

        cash_delta = fill.qty * fill.price
        if fill.side == Side.BUY:
            self.state.cash -= cash_delta
        else:
            self.state.cash += cash_delta

        self.state.position = new_pos
