"""Analytic Hierarchy Process implemented with NumPy from first principles."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from src import CRITERIA, CRITERIA_LABELS

RANDOM_INDEX = {1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32,
                8: 1.41, 9: 1.45, 10: 1.49}


@dataclass(frozen=True)
class AHPResult:
    matrix: np.ndarray
    normalized_matrix: np.ndarray
    weights: np.ndarray
    lambda_max: float
    consistency_index: float
    consistency_ratio: float
    is_consistent: bool


def default_pairwise_matrix() -> np.ndarray:
    """Return a transparent, perfectly consistent example based on stated weights."""
    base_weights = np.array([0.30, 0.25, 0.20, 0.15, 0.10])
    return base_weights[:, None] / base_weights[None, :]


def validate_pairwise_matrix(matrix: np.ndarray, tolerance: float = 1e-8) -> np.ndarray:
    """Validate AHP's square, positive, reciprocal comparison matrix."""
    values = np.asarray(matrix, dtype=float)
    if values.ndim != 2 or values.shape[0] != values.shape[1]:
        raise ValueError("The pairwise-comparison matrix must be square.")
    if values.shape[0] == 0:
        raise ValueError("The pairwise-comparison matrix cannot be empty.")
    if not np.isfinite(values).all() or (values <= 0).any():
        raise ValueError("Pairwise comparisons must be finite positive numbers.")
    if not np.allclose(np.diag(values), 1.0, atol=tolerance):
        raise ValueError("All diagonal pairwise comparisons must equal 1.")
    if not np.allclose(values * values.T, 1.0, atol=tolerance):
        raise ValueError("The matrix must be reciprocal: a_ij × a_ji = 1.")
    return values


def calculate_ahp(matrix: np.ndarray) -> AHPResult:
    """Calculate AHP weights, lambda max, CI and CR using the principal eigenvector."""
    values = validate_pairwise_matrix(matrix)
    column_sums = values.sum(axis=0)
    normalized = values / column_sums
    eigenvalues, eigenvectors = np.linalg.eig(values)
    principal_position = int(np.argmax(eigenvalues.real))
    principal_vector = np.abs(eigenvectors[:, principal_position].real)
    weights = principal_vector / principal_vector.sum()
    lambda_max = float(eigenvalues[principal_position].real)
    count = values.shape[0]
    consistency_index = 0.0 if count == 1 else max(0.0, (lambda_max - count) / (count - 1))
    random_index = RANDOM_INDEX.get(count)
    if random_index is None:
        raise ValueError(f"No random index is configured for a {count}×{count} matrix.")
    consistency_ratio = 0.0 if random_index == 0 else consistency_index / random_index
    return AHPResult(values, normalized, weights, lambda_max, consistency_index,
                     consistency_ratio, consistency_ratio <= 0.10)


def ahp_weight_table(result: AHPResult):
    import pandas as pd
    return pd.DataFrame({"criterion": CRITERIA, "label": CRITERIA_LABELS, "weight": result.weights})
