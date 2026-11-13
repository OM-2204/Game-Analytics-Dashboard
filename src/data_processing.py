from __future__ import annotations
import sqlite3
from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = {"event_id", "player_id", "event_type", "event_timestamp", "revenue"}

def load_events_csv(file_or_path) -> pd.DataFrame:
    """Load event data and normalize timestamp/revenue types."""
    df = pd.read_csv(file_or_path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")
    df = df[list(REQUIRED_COLUMNS)].copy()
    df["event_timestamp"] = pd.to_datetime(df["event_timestamp"], errors="coerce", utc=True)
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
    df["event_id"] = df["event_id"].astype("string")
    df["player_id"] = df["player_id"].astype("string")
    df["event_type"] = df["event_type"].astype("string").str.strip().str.lower()
    return df

def validate_and_clean_events(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Return (clean_events, issue_log). Invalid rows are excluded.
    Duplicate event_id rows are flagged; the first occurrence is retained.
    """
    work = df.copy()
    issues = []

    def flag(mask, issue):
        for idx in work.index[mask.fillna(False)]:
            issues.append({"row_index": int(idx), "issue": issue})

    flag(work["player_id"].isna() | work["player_id"].str.strip().eq(""), "missing_player_id")
    flag(work["event_id"].isna() | work["event_id"].str.strip().eq(""), "missing_event_id")
    flag(work["event_timestamp"].isna(), "invalid_timestamp")
    flag(work["revenue"].isna(), "invalid_revenue")
    flag(work["revenue"].lt(0), "negative_revenue")
    flag(work["event_type"].isna() | work["event_type"].str.strip().eq(""), "missing_event_type")

    invalid_mask = (
        work["player_id"].isna() | work["player_id"].str.strip().eq("") |
        work["event_id"].isna() | work["event_id"].str.strip().eq("") |
        work["event_timestamp"].isna() | work["revenue"].isna() |
        work["revenue"].lt(0) |
        work["event_type"].isna() | work["event_type"].str.strip().eq("")
    )
    clean = work.loc[~invalid_mask].copy()

    duplicate_mask = clean.duplicated(subset=["event_id"], keep="first")
    for idx in clean.index[duplicate_mask]:
        issues.append({"row_index": int(idx), "issue": "duplicate_event_id"})
    clean = clean.loc[~duplicate_mask].copy()

    clean["event_date"] = clean["event_timestamp"].dt.date.astype(str)
    issue_log = pd.DataFrame(issues, columns=["row_index", "issue"])
    return clean.reset_index(drop=True), issue_log

def write_events_to_sqlite(df: pd.DataFrame, db_path: str | Path) -> None:
    """Replace the events table with the supplied cleaned dataset."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        df.to_sql("events", conn, if_exists="replace", index=False)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_player ON events(player_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_date ON events(event_date)")
