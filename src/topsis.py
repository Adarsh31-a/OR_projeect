"""TOPSIS ranking using vector normalization and configurable criterion directions."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class TOPSISResult:
    normalized_matrix: np.ndarray
    weighted_matrix: np.ndarray
    ideal_best: np.ndarray
    ideal_worst: np.ndarray
    distance_to_best: np.ndarray
    distance_to_worst: np.ndarray
    closeness: np.ndarray
    ranked: pd.DataFrame


def _validate_inputs(decision_matrix: np.ndarray, weights: np.ndarray, directions: list[str]) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(decision_matrix, dtype=float)
    criterion_weights = np.asarray(weights, dtype=float)
    if values.ndim != 2 or values.shape[0] == 0 or values.shape[1] == 0:
        raise ValueError("Decision matrix must be a non-empty two-dimensional array.")
    if not np.isfinite(values).all():
        raise ValueError("Decision matrix contains missing or non-finite values.")
    if criterion_weights.ndim != 1 or len(criterion_weights) != values.shape[1]:
        raise ValueError("Weights must contain one value for each criterion.")
    if not np.isfinite(criterion_weights).all() or (criterion_weights < 0).any() or criterion_weights.sum() <= 0:
        raise ValueError("Weights must be finite, non-negative, and have a positive sum.")
    if len(directions) != values.shape[1] or any(direction not in {"benefit", "cost"} for direction in directions):
        raise ValueError("Each criterion direction must be either 'benefit' or 'cost'.")
    return values, criterion_weights / criterion_weights.sum()


def calculate_topsis(
    data: pd.DataFrame,
    criteria: list[str],
    weights: np.ndarray,
    directions: list[str] | None = None,
) -> TOPSISResult:
    """Rank alternatives by closeness to the ideal best and away from the ideal worst."""
    directions = directions or ["benefit"] * len(criteria)
    values, normal_weights = _validate_inputs(data[criteria].to_numpy(), weights, directions)
    norms = np.linalg.norm(values, axis=0)
    normalized = np.divide(values, norms, out=np.zeros_like(values), where=norms != 0)
    weighted = normalized * normal_weights
    benefit_mask = np.array([direction == "benefit" for direction in directions])
    ideal_best = np.where(benefit_mask, weighted.max(axis=0), weighted.min(axis=0))
    ideal_worst = np.where(benefit_mask, weighted.min(axis=0), weighted.max(axis=0))
    distance_to_best = np.linalg.norm(weighted - ideal_best, axis=1)
    distance_to_worst = np.linalg.norm(weighted - ideal_worst, axis=1)
    denominator = distance_to_best + distance_to_worst
    closeness = np.divide(distance_to_worst, denominator, out=np.full(len(values), 0.5), where=denominator != 0)
    ranked = data.copy()
    ranked["topsis_closeness"] = closeness
    ranked["topsis_rank"] = ranked["topsis_closeness"].rank(method="min", ascending=False).astype(int)
    ranked = ranked.sort_values(["topsis_closeness", "application_id"], ascending=[False, True]).reset_index(drop=True)
    return TOPSISResult(normalized, weighted, ideal_best, ideal_worst, distance_to_best,
                        distance_to_worst, closeness, ranked)
