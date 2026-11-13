import pandas as pd
from src.data_processing import validate_and_clean_events
from src.validation import compare_sql_and_pandas
from src.data_processing import write_events_to_sqlite

def test_bad_rows_are_flagged():
    df = pd.DataFrame([
        ["e1","p1","session_start","2026-01-01T10:00:00Z",0],
        ["e2",None,"purchase","2026-01-01T11:00:00Z",5],
        ["e3","p3","purchase","not-a-date",-2],
        ["e1","p1","session_start","2026-01-01T10:00:00Z",0],
    ], columns=["event_id","player_id","event_type","event_timestamp","revenue"])
    df["event_timestamp"] = pd.to_datetime(df["event_timestamp"], errors="coerce", utc=True)
    clean, issues = validate_and_clean_events(df)
    assert len(clean) == 1
    assert set(issues["issue"]) >= {"missing_player_id", "invalid_timestamp", "negative_revenue", "duplicate_event_id"}

def test_sql_pandas_reconciliation(sample_events, tmp_path):
    db = tmp_path / "events.db"
    write_events_to_sqlite(sample_events, db)
    result = compare_sql_and_pandas(sample_events, str(db))
    assert result["passed"] is True
