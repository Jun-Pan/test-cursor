import unittest

from quant_system.config import SystemConfig
from quant_system.research.backtest import generate_synthetic_ticks, run_backtest


class BacktestTests(unittest.TestCase):
    def test_backtest_produces_result(self) -> None:
        config = SystemConfig()
        ticks = generate_synthetic_ticks(config.data.symbol, n_ticks=200, seed_price=100.0)
        result = run_backtest(config, ticks)
        self.assertEqual(result.total_ticks, 200)
        self.assertGreaterEqual(result.total_trades, 0)
        self.assertIsInstance(result.realized_pnl, float)
        self.assertIsInstance(result.equity, float)


if __name__ == "__main__":
    unittest.main()
