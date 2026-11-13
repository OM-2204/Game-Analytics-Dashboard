from __future__ import annotations
import sqlite3
import pandas as pd

def _active_events(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["event_type"].isin(["session_start", "level_complete", "purchase", "app_open"])].copy()

def calculate_kpis_pandas(df: pd.DataFrame) -> dict:
    """Independent Pandas implementation of headline KPIs."""
    active = _active_events(df)
    dau = int(active["player_id"].nunique())
    revenue = float(df.loc[df["event_type"].eq("purchase"), "revenue"].sum())
    paying_users = int(df.loc[(df["event_type"].eq("purchase")) & (df["revenue"] > 0), "player_id"].nunique())
    arpu = revenue / dau if dau else 0.0
    arppu = revenue / paying_users if paying_users else 0.0
    return {
        "active_users": dau,
        "total_revenue": revenue,
        "paying_users": paying_users,
        "arpu": arpu,
        "arppu": arppu,
    }

def calculate_kpis_sql(db_path: str) -> dict:
    """SQL implementation of the same KPIs for cross-checking."""
    query = """
    SELECT
      (SELECT COUNT(DISTINCT player_id) FROM events
       WHERE event_type IN ('session_start','level_complete','purchase','app_open')) AS active_users,
      (SELECT COALESCE(SUM(revenue), 0) FROM events WHERE event_type='purchase') AS total_revenue,
      (SELECT COUNT(DISTINCT player_id) FROM events
       WHERE event_type='purchase' AND revenue > 0) AS paying_users
    """
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(query).fetchone()
    active_users, revenue, paying_users = row
    return {
        "active_users": int(active_users),
        "total_revenue": float(revenue),
        "paying_users": int(paying_users),
        "arpu": float(revenue) / active_users if active_users else 0.0,
        "arppu": float(revenue) / paying_users if paying_users else 0.0,
    }

def daily_metrics(df: pd.DataFrame) -> pd.DataFrame:
    active = _active_events(df)
    dau = active.groupby("event_date")["player_id"].nunique().rename("DAU")
    revenue = df[df["event_type"].eq("purchase")].groupby("event_date")["revenue"].sum().rename("Revenue")
    result = pd.concat([dau, revenue], axis=1).fillna(0).reset_index()
    return result.sort_values("event_date")

def retention_table(df: pd.DataFrame, max_day: int = 30) -> pd.DataFrame:
    """
    Calendar-day cohort retention.
    D1 means a player active exactly one calendar day after their first active date.
    D7 and D30 use the same exact-day definition.
    """
    active = _active_events(df)
    if active.empty:
        return pd.DataFrame(columns=["cohort_date", "cohort_size"] + [f"D{i}" for i in (1,7,30) if i <= max_day])
    active = active[["player_id", "event_date"]].drop_duplicates().copy()
    active["event_date"] = pd.to_datetime(active["event_date"])
    first = active.groupby("player_id")["event_date"].min().rename("cohort_date")
    active = active.join(first, on="player_id")
    active["days_since_cohort"] = (active["event_date"] - active["cohort_date"]).dt.days
    rows = []
    for cohort_date, group in active.groupby("cohort_date"):
        cohort_players = set(group.loc[group["days_since_cohort"].eq(0), "player_id"])
        size = len(cohort_players)
        row = {"cohort_date": str(cohort_date.date()), "cohort_size": size}
        for day in (1, 7, 30):
            if day <= max_day:
                returned = set(group.loc[group["days_since_cohort"].eq(day), "player_id"])
                row[f"D{day}"] = len(returned) / size if size else 0.0
        rows.append(row)
    return pd.DataFrame(rows).sort_values("cohort_date")

def event_mix(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("event_type").size().rename("events").reset_index().sort_values("events", ascending=False)
