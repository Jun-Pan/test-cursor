from __future__ import annotations


class MeanReversionModel:
    """
    Very small baseline model:
    - score > 0 suggests mean-reversion sell edge
    - score < 0 suggests mean-reversion buy edge
    """

    def predict_score(self, features: dict[str, float]) -> float:
        z = features["zscore"]
        vol = max(features["vol"], 1e-6)
        # Penalize scores in high volatility regimes.
        return -z / (1 + (vol * 200))
