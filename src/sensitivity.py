"""Reproducible sensitivity analyses for ranking stability."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.topsis import calculate_topsis


def spearman_rank_correlation(first: pd.Series, second: pd.Series) -> float:
    """Calculate Spearman correlation without a SciPy dependency."""
    return float(first.rank(method="average").corr(second.rank(method="average"), method="pearson"))


def compare_rankings(baseline: pd.DataFrame, alternative: pd.DataFrame) -> tuple[pd.DataFrame, float, int]:
    """Align two TOPSIS outputs and quantify agreement with Spearman correlation."""
    compared = baseline[["application_id", "topsis_rank", "topsis_closeness"]].merge(
        alternative[["application_id", "topsis_rank", "topsis_closeness"]], on="application_id",
        suffixes=("_original", "_new"), validate="one_to_one"
    )
    compared["rank_change"] = compared["topsis_rank_new"] - compared["topsis_rank_original"]
    correlation = spearman_rank_correlation(compared["topsis_rank_original"], compared["topsis_rank_new"])
    original_top = set(compared.nsmallest(5, "topsis_rank_original")["application_id"])
    new_top = set(compared.nsmallest(5, "topsis_rank_new")["application_id"])
    return compared.sort_values("topsis_rank_original"), correlation, len(original_top & new_top)


def weight_sensitivity(
    data: pd.DataFrame, criteria: list[str], original_weights: np.ndarray,
    adjusted_weights: np.ndarray, directions: list[str] | None = None,
) -> dict:
    """Rerun TOPSIS after directly changing final weights, preserving their total at one."""
    baseline = calculate_topsis(data, criteria, original_weights, directions)
    adjusted = np.asarray(adjusted_weights, dtype=float)
    if (adjusted < 0).any() or adjusted.sum() <= 0:
        raise ValueError("Adjusted weights must be non-negative and sum to a positive value.")
    adjusted = adjusted / adjusted.sum()
    changed = calculate_topsis(data, criteria, adjusted, directions)
    comparison, correlation, overlap = compare_rankings(baseline.ranked, changed.ranked)
    return {"adjusted_weights": adjusted, "baseline": baseline.ranked, "new": changed.ranked,
            "comparison": comparison, "spearman_correlation": correlation, "top_five_overlap": overlap}


def score_perturbation_analysis(
    data: pd.DataFrame, criteria: list[str], weights: np.ndarray, perturbation: float = 0.5,
    iterations: int = 100, seed: int = 2026,
) -> pd.DataFrame:
    """Estimate ranking stability after bounded, reproducible score noise.

    Scores remain on the documented 1--10 scale for every simulation.
    """
    if perturbation < 0 or iterations < 1:
        raise ValueError("perturbation must be non-negative and iterations must be at least one.")
    baseline = calculate_topsis(data, criteria, weights).ranked
    random_generator = np.random.default_rng(seed)
    records = []
    for iteration in range(1, iterations + 1):
        perturbed = data.astype({criterion: float for criterion in criteria}).copy()
        noise = random_generator.uniform(-perturbation, perturbation, size=(len(data), len(criteria)))
        perturbed.loc[:, criteria] = np.clip(perturbed[criteria].to_numpy(float) + noise, 1, 10)
        rerun = calculate_topsis(perturbed, criteria, weights).ranked
        _, correlation, overlap = compare_rankings(baseline, rerun)
        records.append({"iteration": iteration, "spearman_correlation": correlation,
                        "top_five_overlap": overlap, "perturbation": perturbation, "seed": seed})
    return pd.DataFrame(records)
