import pandas as pd
import pytest
from src.data_processing import validate_and_clean_events, write_events_to_sqlite

@pytest.fixture
def sample_events():
    df = pd.DataFrame([
        ["e1","p1","session_start","2026-01-01T10:00:00Z",0.0],
        ["e2","p1","session_start","2026-01-02T10:00:00Z",0.0],
        ["e3","p2","session_start","2026-01-01T11:00:00Z",0.0],
        ["e4","p2","purchase","2026-01-01T11:10:00Z",10.0],
        ["e5","p3","app_open","2026-01-01T12:00:00Z",0.0],
    ], columns=["event_id","player_id","event_type","event_timestamp","revenue"])
    df["event_timestamp"] = pd.to_datetime(df["event_timestamp"], utc=True)
    df["event_date"] = df["event_timestamp"].dt.date.astype(str)
    return df

@pytest.fixture
def sqlite_db(tmp_path, sample_events):
    path = tmp_path / "test.db"
    write_events_to_sqlite(sample_events, path)
    return str(path)
