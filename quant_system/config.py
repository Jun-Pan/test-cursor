from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DataConfig:
    symbol: str = "BTCUSDT"
    tick_interval_seconds: float = 0.05
    seed_price: float = 100.0


@dataclass(frozen=True)
class StorageConfig:
    db_path: Path = Path("quant_system.db")


@dataclass(frozen=True)
class ModelConfig:
    window_size: int = 30
    zscore_threshold: float = 0.5


@dataclass(frozen=True)
class RiskConfig:
    max_abs_position: float = 5.0
    max_order_size: float = 1.0
    max_daily_loss: float = 200.0


@dataclass(frozen=True)
class ExecutionConfig:
    starting_cash: float = 50_000.0


@dataclass(frozen=True)
class SystemConfig:
    data: DataConfig = DataConfig()
    storage: StorageConfig = StorageConfig()
    model: ModelConfig = ModelConfig()
    risk: RiskConfig = RiskConfig()
    execution: ExecutionConfig = ExecutionConfig()
