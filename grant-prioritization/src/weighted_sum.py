"""A transparent weighted-sum comparator for the same decision criteria."""

from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_weighted_sum(data: pd.DataFrame, criteria: list[str], weights: np.ndarray) -> pd.DataFrame:
    """Vector-normalize criteria, then add their AHP-weighted values.

    This keeps the scale treatment comparable to TOPSIS while using additive aggregation.
    """
    values = data[criteria].to_numpy(dtype=float)
    normalized_weights = np.asarray(weights, dtype=float)
    if len(normalized_weights) != len(criteria) or (normalized_weights < 0).any() or normalized_weights.sum() <= 0:
        raise ValueError("Weights must be non-negative, match the criteria, and sum to a positive value.")
    normalized_weights = normalized_weights / normalized_weights.sum()
    norms = np.linalg.norm(values, axis=0)
    normalized = np.divide(values, norms, out=np.zeros_like(values), where=norms != 0)
    result = data.copy()
    result["weighted_sum_score"] = normalized @ normalized_weights
    result["weighted_sum_rank"] = result["weighted_sum_score"].rank(method="min", ascending=False).astype(int)
    return result.sort_values(["weighted_sum_score", "application_id"], ascending=[False, True]).reset_index(drop=True)
