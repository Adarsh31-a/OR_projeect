import numpy as np
import pytest

from src.ahp import calculate_ahp, default_pairwise_matrix, validate_pairwise_matrix


def test_ahp_weights_sum_to_one_and_are_nonnegative():
    result = calculate_ahp(default_pairwise_matrix())
    assert np.isclose(result.weights.sum(), 1.0)
    assert (result.weights >= 0).all()


def test_perfectly_consistent_matrix_has_zero_consistency_ratio():
    result = calculate_ahp(default_pairwise_matrix())
    assert result.consistency_ratio == pytest.approx(0.0, abs=1e-10)
    assert result.is_consistent


def test_inconsistent_matrix_is_flagged():
    matrix = np.array([[1, 9, 1 / 9], [1 / 9, 1, 9], [9, 1 / 9, 1]], dtype=float)
    result = calculate_ahp(matrix)
    assert result.consistency_ratio > 0.10
    assert not result.is_consistent


def test_nonreciprocal_matrix_fails_with_message():
    with pytest.raises(ValueError, match="reciprocal"):
        validate_pairwise_matrix(np.array([[1, 2], [2, 1]], dtype=float))
