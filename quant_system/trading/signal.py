from __future__ import annotations

from datetime import datetime

from quant_system.core.types import Side, Signal


class SignalGenerator:
    def __init__(self, threshold: float) -> None:
        self.threshold = threshold

    def generate(self, symbol: str, ts: datetime, score: float) -> Signal:
        if score >= self.threshold:
            return Signal(symbol=symbol, ts=ts, side=Side.SELL, confidence=min(abs(score), 5.0), reason="zscore_high")
        if score <= -self.threshold:
            return Signal(symbol=symbol, ts=ts, side=Side.BUY, confidence=min(abs(score), 5.0), reason="zscore_low")
        return Signal(symbol=symbol, ts=ts, side=None, confidence=abs(score), reason="no_edge")
