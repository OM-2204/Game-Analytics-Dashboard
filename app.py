from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_processing import load_events_csv, validate_and_clean_events, write_events_to_sqlite
from src.analytics import calculate_kpis_pandas, daily_metrics, retention_table, event_mix
from src.validation import compare_sql_and_pandas, summarize_data_quality
from src.report_generator import build_markdown_report, save_report

st.set_page_config(page_title="Game Analytics Agent", page_icon="🎮", layout="wide")
st.title("🎮 Game Analytics Agent")
st.caption("An AI-assisted analytics project: game KPIs, data-quality checks, SQL/Pandas reconciliation and automated reporting.")

DEFAULT_DATA = Path("data/game_events.csv")
uploaded = st.sidebar.file_uploader("Upload game event CSV", type=["csv"])
st.sidebar.info("Expected columns: event_id, player_id, event_type, event_timestamp, revenue")

try:
    raw = load_events_csv(uploaded if uploaded is not None else DEFAULT_DATA)
except Exception as exc:
    st.error(f"Could not load dataset: {exc}")
    st.stop()

clean, issues = validate_and_clean_events(raw)
db_path = "data/game_analytics.db"
write_events_to_sqlite(clean, db_path)

if clean.empty:
    st.warning("No valid records remain after data-quality checks.")
    st.stop()

kpis = calculate_kpis_pandas(clean)
validation = compare_sql_and_pandas(clean, db_path)
quality = summarize_data_quality(raw, clean, issues)
daily = daily_metrics(clean)
retention = retention_table(clean)

st.sidebar.markdown("---")
st.sidebar.metric("Rows loaded", f"{len(raw):,}")
st.sidebar.metric("Rows retained", f"{len(clean):,}")
st.sidebar.metric("Issues flagged", f"{len(issues):,}")

st.subheader("Key performance indicators")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Active users", f"{kpis['active_users']:,}")
c2.metric("Purchase revenue", f"₹{kpis['total_revenue']:,.2f}")
c3.metric("Paying users", f"{kpis['paying_users']:,}")
c4.metric("ARPU", f"₹{kpis['arpu']:,.2f}")
c5.metric("ARPPU", f"₹{kpis['arppu']:,.2f}")

tab1, tab2, tab3, tab4 = st.tabs(["Trends", "Retention", "Data quality", "Validation & report"])

with tab1:
    st.subheader("Daily activity and revenue")
    if not daily.empty:
        fig = px.line(daily, x="event_date", y="DAU", markers=True, title="Daily Active Users")
        st.plotly_chart(fig, use_container_width=True)
        rev = px.bar(daily, x="event_date", y="Revenue", title="Daily purchase revenue")
        st.plotly_chart(rev, use_container_width=True)
    st.subheader("Event mix")
    st.plotly_chart(px.pie(event_mix(clean), names="event_type", values="events", title="Events by type"), use_container_width=True)

with tab2:
    st.subheader("Player retention by first-active-date cohort")
    st.caption("D1/D7/D30 mean activity exactly 1, 7 or 30 calendar days after the player's first active date. Recent cohorts may not yet have a full observation window.")
    if not retention.empty:
        display = retention.copy()
        for col in ["D1", "D7", "D30"]:
            if col in display:
                display[col] = (display[col] * 100).round(1).astype(str) + "%"
        st.dataframe(display, use_container_width=True, hide_index=True)
    else:
        st.info("No retention cohorts available.")

with tab3:
    st.subheader("Data-quality summary")
    st.json(quality)
    if not issues.empty:
        st.dataframe(issues, use_container_width=True, hide_index=True)
    else:
        st.success("No data-quality issues detected.")

with tab4:
    st.subheader("Independent SQL vs Pandas validation")
    if validation["passed"]:
        st.success("All KPI reconciliation checks passed.")
    else:
        st.error("At least one KPI reconciliation check failed.")
    st.json(validation)
    report = build_markdown_report(kpis, daily, validation, quality)
    st.download_button("Download analytics report (Markdown)", report, file_name="game_analytics_report.md", mime="text/markdown")
    if st.button("Save report to project folder"):
        path = save_report(report)
        st.success(f"Report saved to {path}")

st.markdown("---")
st.caption("Definitions: ARPU = purchase revenue / distinct active users in the loaded dataset. ARPPU = purchase revenue / distinct paying users. Retention uses exact calendar-day return.")
