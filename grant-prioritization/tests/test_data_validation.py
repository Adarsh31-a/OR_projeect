import pandas as pd
import pytest

from src import CRITERIA
from src.data_validation import validate_grant_dataframe


def valid_frame():
    return pd.DataFrame({
        "application_id": ["A-1", "A-2"], "project_name": ["One", "Two"],
        "region": ["North", "South"], "sector": ["Education", "Healthcare"],
        "requested_amount": [1000, 2000], **{criterion: [5, 8] for criterion in CRITERIA}
    })


def test_missing_and_duplicate_ids_are_detected():
    frame = valid_frame()
    frame.loc[1, "application_id"] = "A-1"
    frame.loc[0, "poverty_reduction_score"] = None
    report = validate_grant_dataframe(frame, raise_on_error=False)
    assert not report["valid"]
    assert report["duplicate_application_ids"] == 1
    assert any("Missing values" in error for error in report["errors"])
    with pytest.raises(ValueError, match="duplicate"):
        validate_grant_dataframe(frame)


def test_invalid_score_is_detected():
    frame = valid_frame()
    frame.loc[0, "beneficiaries_score"] = 11
    with pytest.raises(ValueError, match="1--10"):
        validate_grant_dataframe(frame)
