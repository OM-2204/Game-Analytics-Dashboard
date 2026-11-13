from src.analytics import calculate_kpis_pandas, calculate_kpis_sql, retention_table

def test_kpis(sample_events, sqlite_db):
    result = calculate_kpis_pandas(sample_events)
    assert result["active_users"] == 3
    assert result["total_revenue"] == 10.0
    assert result["paying_users"] == 1
    assert result["arpu"] == 10.0 / 3
    assert result == calculate_kpis_sql(sqlite_db)

def test_d1_retention_exact_calendar_day(sample_events):
    result = retention_table(sample_events)
    day_one = result.loc[result["cohort_date"].eq("2026-01-01"), "D1"].iloc[0]
    assert day_one == 1 / 3
