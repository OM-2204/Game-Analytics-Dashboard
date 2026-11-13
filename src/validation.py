from __future__ import annotations
import math
import pandas as pd
from .analytics import calculate_kpis_pandas, calculate_kpis_sql

def compare_sql_and_pandas(df: pd.DataFrame, db_path: str) -> dict:
    pandas_result = calculate_kpis_pandas(df)
    sql_result = calculate_kpis_sql(db_path)
    checks = {}
    for key in pandas_result:
        a, b = pandas_result[key], sql_result[key]
        checks[key] = math.isclose(float(a), float(b), rel_tol=1e-9, abs_tol=1e-9)
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "pandas": pandas_result,
        "sql": sql_result,
    }

def summarize_data_quality(raw_df: pd.DataFrame, clean_df: pd.DataFrame, issue_log: pd.DataFrame) -> dict:
    return {
        "raw_rows": int(len(raw_df)),
        "clean_rows": int(len(clean_df)),
        "excluded_or_duplicate_rows": int(len(raw_df) - len(clean_df)),
        "issues_found": int(len(issue_log)),
        "issue_counts": issue_log["issue"].value_counts().to_dict() if not issue_log.empty else {},
    }
