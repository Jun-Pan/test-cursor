from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from quant_system.config import SystemConfig
from quant_system.core.types import MarketTick
from quant_system.data.cleaner import TickCleaner
from quant_system.research.features import FeatureEngineer
from quant_system.research.model import MeanReversionModel
from quant_system.trading.execution import SimulatedExecutionEngine
from quant_system.trading.risk import RiskManager
from quant_system.trading.signal import SignalGenerator


@dataclass
class BacktestResult:
    total_ticks: int
    total_trades: int
    realized_pnl: float
    equity: float
    position: float


def generate_synthetic_ticks(symbol: str, n_ticks: int, seed_price: float = 100.0) -> list[MarketTick]:
    from random import gauss, lognormvariate

    ticks: list[MarketTick] = []
    price = seed_price
    start = datetime.now(tz=UTC)
    for idx in range(n_ticks):
        price = max(0.1, price * (1 + gauss(0.0001, 0.01)))
        ticks.append(
            MarketTick(
                symbol=symbol,
                ts=start + timedelta(seconds=idx),
                price=round(price, 6),
                volume=round(max(0.01, lognormvariate(-0.1, 0.5)), 6),
            )
        )
    return ticks


def run_backtest(config: SystemConfig, ticks: list[MarketTick]) -> BacktestResult:
    cleaner = TickCleaner()
    fe = FeatureEngineer()
    model = MeanReversionModel()
    signal_gen = SignalGenerator(config.model.zscore_threshold)
    risk = RiskManager(config.risk)
    execution = SimulatedExecutionEngine(config.execution)

    rolling_window: list[MarketTick] = []
    trades = 0
    for tick in ticks:
        cleaned = cleaner.clean(tick)
        if cleaned is None:
            continue

        rolling_window.append(cleaned)
        rolling_window = rolling_window[-config.model.window_size :]
        features = fe.build(rolling_window)
        if features is None:
            continue

        score = model.predict_score(features)
        signal = signal_gen.generate(cleaned.symbol, cleaned.ts, score)
        qty = risk.check(
            signal=signal,
            current_position=execution.state.position,
            mark_price=cleaned.price,
            realized_pnl=execution.state.realized_pnl,
        )
        if qty <= 0:
            execution.state.mark_to_market(cleaned.price)
            continue

        execution.place_and_fill(cleaned.symbol, cleaned.ts, signal.side, qty, cleaned.price)
        execution.state.mark_to_market(cleaned.price)
        trades += 1

    if ticks:
        execution.state.mark_to_market(ticks[-1].price)
    return BacktestResult(
        total_ticks=len(ticks),
        total_trades=trades,
        realized_pnl=round(execution.state.realized_pnl, 4),
        equity=round(execution.state.equity, 4),
        position=round(execution.state.position, 6),
    )
