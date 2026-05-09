from __future__ import annotations

import time
from dataclasses import dataclass

from quant_system.config import SystemConfig
from quant_system.core.events import EventBus
from quant_system.core.types import MarketTick
from quant_system.data.cleaner import TickCleaner
from quant_system.data.collector import MockPriceCollector
from quant_system.data.storage import SQLiteStorage
from quant_system.research.features import FeatureEngineer
from quant_system.research.model import MeanReversionModel
from quant_system.trading.execution import SimulatedExecutionEngine
from quant_system.trading.risk import RiskManager
from quant_system.trading.signal import SignalGenerator


@dataclass
class LiveRunStats:
    ticks_processed: int = 0
    orders_sent: int = 0
    fills: int = 0


class LiveTradingSystem:
    def __init__(self, config: SystemConfig) -> None:
        self.config = config
        self.bus = EventBus()
        self.collector = MockPriceCollector(
            symbol=config.data.symbol,
            seed_price=config.data.seed_price,
        )
        self.cleaner = TickCleaner()
        self.storage = SQLiteStorage(config.storage.db_path)
        self.fe = FeatureEngineer()
        self.model = MeanReversionModel()
        self.signal_gen = SignalGenerator(config.model.zscore_threshold)
        self.risk = RiskManager(config.risk)
        self.execution = SimulatedExecutionEngine(config.execution)
        self.stats = LiveRunStats()

    def on_tick(self, tick: MarketTick) -> None:
        cleaned = self.cleaner.clean(tick)
        if cleaned is None:
            return

        self.storage.insert_tick(cleaned)
        self.stats.ticks_processed += 1
        self.bus.publish("tick", {"tick": cleaned})

        window = self.storage.get_recent_ticks(cleaned.symbol, self.config.model.window_size)
        features = self.fe.build(window)
        if features is None:
            return

        score = self.model.predict_score(features)
        signal = self.signal_gen.generate(cleaned.symbol, cleaned.ts, score)
        self.bus.publish("signal", {"signal": signal, "score": score})

        qty = self.risk.check(
            signal=signal,
            current_position=self.execution.state.position,
            mark_price=cleaned.price,
            realized_pnl=self.execution.state.realized_pnl,
        )
        if qty <= 0:
            self.execution.state.mark_to_market(cleaned.price)
            return

        order, fill = self.execution.place_and_fill(
            symbol=cleaned.symbol,
            ts=cleaned.ts,
            side=signal.side,
            qty=qty,
            price=cleaned.price,
        )
        self.storage.insert_order(order)
        self.storage.insert_fill(fill)
        self.execution.state.mark_to_market(cleaned.price)
        self.stats.orders_sent += 1
        self.stats.fills += 1
        self.bus.publish("fill", {"fill": fill, "state": self.execution.state})

    def run(self, n_ticks: int = 300) -> LiveRunStats:
        for _ in range(n_ticks):
            tick = self.collector.collect_next()
            self.on_tick(tick)
            time.sleep(self.config.data.tick_interval_seconds)
        return self.stats

    def close(self) -> None:
        self.storage.close()
