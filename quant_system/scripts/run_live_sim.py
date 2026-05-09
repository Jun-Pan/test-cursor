from quant_system.config import SystemConfig
from quant_system.trading.live_engine import LiveTradingSystem


def main() -> None:
    config = SystemConfig()
    system = LiveTradingSystem(config)
    try:
        stats = system.run(n_ticks=120)
        state = system.execution.state
        print("=== Live Simulation Summary ===")
        print(f"ticks_processed: {stats.ticks_processed}")
        print(f"orders_sent: {stats.orders_sent}")
        print(f"fills: {stats.fills}")
        print(f"cash: {round(state.cash, 4)}")
        print(f"position: {round(state.position, 6)}")
        print(f"realized_pnl: {round(state.realized_pnl, 4)}")
        print(f"unrealized_pnl: {round(state.unrealized_pnl, 4)}")
        print(f"equity: {round(state.equity, 4)}")
    finally:
        system.close()


if __name__ == "__main__":
    main()
