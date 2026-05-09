from quant_system.config import SystemConfig
from quant_system.research.backtest import generate_synthetic_ticks, run_backtest


def main() -> None:
    config = SystemConfig()
    ticks = generate_synthetic_ticks(
        symbol=config.data.symbol,
        n_ticks=2000,
        seed_price=config.data.seed_price,
    )
    result = run_backtest(config, ticks)
    print("=== Backtest Result ===")
    print(f"ticks: {result.total_ticks}")
    print(f"trades: {result.total_trades}")
    print(f"realized_pnl: {result.realized_pnl}")
    print(f"equity: {result.equity}")
    print(f"position: {result.position}")


if __name__ == "__main__":
    main()
