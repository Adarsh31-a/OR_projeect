"""CSV input utilities."""

from __future__ import annotations

from pathlib import Path
import pandas as pd

from src.data_validation import validate_grant_dataframe


def load_grant_applications(path: str | Path) -> pd.DataFrame:
    """Load and validate a grant application CSV without changing the data."""
    dataframe = pd.read_csv(path)
    validate_grant_dataframe(dataframe)
    return dataframe
