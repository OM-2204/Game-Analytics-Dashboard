# Game Analytics Agent

A portfolio MVP demonstrating analytics, AI-assisted development, data-quality controls, independent metric validation and automated reporting for a fictional mobile game.

## Features
- DAU, purchase revenue, paying users, ARPU and ARPPU
- Exact calendar-day D1, D7 and D30 retention cohorts
- Daily activity and revenue charts
- Data-quality checks for missing IDs, invalid timestamps, invalid/negative revenue and duplicate event IDs
- Independent SQL vs Pandas reconciliation for headline KPIs
- Downloadable Markdown report
- Pytest unit tests with manually checkable expected values

## Important metric definitions
- Active user: distinct player with at least one `session_start`, `level_complete`, `purchase` or `app_open` event.
- Revenue: sum of `revenue` on `purchase` events only.
- ARPU: purchase revenue divided by distinct active users in the loaded dataset.
- ARPPU: purchase revenue divided by distinct players with positive purchase revenue.
- D1/D7/D30: share of a cohort active exactly 1/7/30 calendar days after its first active date.

These are deliberately explicit project definitions. Real game companies may use different event and revenue definitions.

## Setup (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Run tests
```powershell
pytest -q
```

## Dataset
`data/game_events.csv` is a synthetic demonstration dataset. It is not real player data and should not be represented as real company data.

CSV columns:
`event_id, player_id, event_type, event_timestamp, revenue`

## Project limitations
- No live game telemetry or production database connection.
- No causal explanation for metric changes.
- No LLM-generated SQL execution in this first version; the analytics are deterministic and predefined by design.
- The report provides descriptive observations, not business-causal conclusions.

## How to demonstrate validation
1. Open the Validation & report tab.
2. Show the SQL/Pandas reconciliation.
3. Run `pytest -q` in the VS Code terminal.
4. Explain that KPI calculations are implemented independently in SQL and Pandas and compared.
5. Explain the synthetic test fixture and the expected 33.3% D1 retention for the Jan 1 cohort (one of three players returned on Jan 2).
