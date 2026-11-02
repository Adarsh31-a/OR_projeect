import numpy as np
import pandas as pd
import pytest

from src.topsis import calculate_topsis


CRITERIA = ["one", "two"]


def test_topsis_scores_are_finite_bounded_and_ranked():
    data = pd.DataFrame({"application_id": ["A", "B", "C"], "one": [9, 5, 1], "two": [8, 6, 2]})
    result = calculate_topsis(data, CRITERIA, np.array([0.5, 0.5]))
    scores = result.ranked["topsis_closeness"].to_numpy()
    assert np.isfinite(scores).all()
    assert ((scores >= 0) & (scores <= 1)).all()
    assert result.ranked["topsis_closeness"].is_monotonic_decreasing


def test_zero_column_does_not_divide_by_zero():
    data = pd.DataFrame({"application_id": ["A", "B"], "one": [0, 0], "two": [2, 8]})
    result = calculate_topsis(data, CRITERIA, np.array([0.4, 0.6]))
    assert np.isfinite(result.closeness).all()


def test_invalid_weights_raise_informative_error():
    data = pd.DataFrame({"application_id": ["A"], "one": [1], "two": [2]})
    with pytest.raises(ValueError, match="Weights"):
        calculate_topsis(data, CRITERIA, np.array([0, 0]))
