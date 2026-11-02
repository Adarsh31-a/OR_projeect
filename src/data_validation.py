"""Validation for included and user-uploaded grant application CSV files."""

from __future__ import annotations

import pandas as pd

from src import CRITERIA

REQUIRED_COLUMNS = [
    "application_id", "project_name", "region", "sector", "requested_amount", *CRITERIA
]


def validate_grant_dataframe(dataframe: pd.DataFrame, raise_on_error: bool = True) -> dict:
    """Return data-quality checks, optionally raising a readable validation error.

    Scores use a 1--10 scale and requested funding must be strictly positive.
    """
    errors: list[str] = []
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in dataframe.columns]
    if missing_columns:
        errors.append("Missing required columns: " + ", ".join(missing_columns))
    if not missing_columns:
        missing_by_column = dataframe[REQUIRED_COLUMNS].isna().sum()
        missing = missing_by_column[missing_by_column > 0].to_dict()
        if missing:
            errors.append(f"Missing values found: {missing}")
        if dataframe["application_id"].astype(str).str.strip().eq("").any():
            errors.append("application_id contains blank values.")
        duplicate_ids = dataframe["application_id"].duplicated().sum()
        if duplicate_ids:
            errors.append(f"Found {duplicate_ids} duplicate application_id value(s).")
        for column in ["requested_amount", *CRITERIA]:
            converted = pd.to_numeric(dataframe[column], errors="coerce")
            if converted.isna().any():
                errors.append(f"{column} must contain numeric values.")
                continue
            if column == "requested_amount" and (converted <= 0).any():
                errors.append("requested_amount must be greater than zero.")
            if column in CRITERIA and ((converted < 1) | (converted > 10)).any():
                errors.append(f"{column} must be on the 1--10 scale.")
    report = {
        "rows": len(dataframe),
        "columns": len(dataframe.columns),
        "missing_values": int(dataframe.isna().sum().sum()),
        "duplicate_application_ids": int(dataframe["application_id"].duplicated().sum())
        if "application_id" in dataframe else None,
        "errors": errors,
        "valid": not errors,
    }
    if errors and raise_on_error:
        raise ValueError("Dataset validation failed:\n- " + "\n- ".join(errors))
    return report
