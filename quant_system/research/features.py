from __future__ import annotations

from statistics import fmean, pstdev

from quant_system.core.types import MarketTick


class FeatureEngineer:
    """Build simple statistical features for short-horizon trading."""

    def build(self, ticks: list[MarketTick]) -> dict[str, float] | None:
        if len(ticks) < 2:
            return None

        prices = [tick.price for tick in ticks]
        returns = [(b / a) - 1 for a, b in zip(prices[:-1], prices[1:])]
        mean_ret = fmean(returns)
        vol = pstdev(returns) if len(returns) > 1 else 0.0
        last_price = prices[-1]
        rolling_mean = fmean(prices)
        zscore = (last_price - rolling_mean) / max(1e-9, pstdev(prices) if len(prices) > 1 else 1)

        return {
            "last_price": last_price,
            "mean_ret": mean_ret,
            "vol": vol,
            "rolling_mean": rolling_mean,
            "zscore": zscore,
        }
