# 🎮 Game Analytics Agent

**An AI-assisted game analytics dashboard for player engagement, retention, revenue, and data-quality monitoring.**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://game-analytics-dashboard-lydumca8dkja46wmdtjgef.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)

**Live application:** https://game-analytics-dashboard-lydumca8dkja46wmdtjgef.streamlit.app/

---

## 1. Project Overview

Game Analytics Agent is a Python-based analytics application designed to help a game team explore player activity, retention, and in-game purchase performance from event-level data.

Users can upload a game-event CSV and view key performance indicators, daily activity and revenue trends, player-retention cohorts, data-quality findings, and an automatically generated analytics report.

The project also demonstrates a validation-first approach: headline metrics are calculated independently using Pandas and SQL, then compared to check whether both implementations produce matching results.

> **Project scope:** This is a portfolio demonstration built with synthetic game-event data. It is not connected to a live game, production telemetry, or a real company's player database.

## 2. Live Demo

Open the deployed application:

**[Launch Game Analytics Agent](https://game-analytics-dashboard-lydumca8dkja46wmdtjgef.streamlit.app/)**

To try it:
1. Open the live application.
2. Upload a CSV file using the sidebar, or use the bundled sample dataset when running locally.
3. Explore the Trends, Retention, Data quality, and Validation & report tabs.
4. Download the generated Markdown report from the report section.

## 3. Features

### Game performance analytics
- **Active users:** Distinct players with at least one qualifying activity event in the uploaded dataset.
- **Purchase revenue:** Sum of revenue recorded on `purchase` events.
- **Paying users:** Distinct players with a positive purchase event.
- **ARPU:** Purchase revenue divided by distinct active users.
- **ARPPU:** Purchase revenue divided by distinct paying users.

### Player activity and retention
- Daily Active Users (DAU) trend.
- Daily purchase-revenue trend.
- Event-type distribution.
- D1, D7, and D30 cohort-retention table.

### Data-quality checks
The application checks for:
- Missing player IDs.
- Missing event IDs.
- Missing event types.
- Invalid timestamps.
- Missing or non-numeric revenue.
- Negative revenue.
- Duplicate event IDs.

Invalid records are excluded from the cleaned dataset, and detected issues are shown in the Data quality tab.

### SQL and Pandas reconciliation
The headline KPIs are implemented separately using:
- Pandas calculations.
- SQL queries executed against a SQLite database.

The application compares the two sets of results and reports whether the values match. This is a consistency check between two implementations; it does not by itself prove that the business definitions or source data are correct.

### Automated reporting
Generate and download a Markdown report containing:
- Headline KPIs.
- A simple first-date-to-last-date revenue comparison.
- Data-quality counts.
- SQL/Pandas validation status.
- An interpretation note describing the limits of the analysis.

## 4. Technology Stack

| Area | Tools |
|---|---|
| Programming language | Python |
| Dashboard | Streamlit |
| Data manipulation | Pandas |
| Database and SQL | SQLite |
| Visualizations | Plotly |
| Testing | Pytest |
| Development assistance | ChatGPT |
| Deployment | Streamlit Community Cloud |

## 5. Application Workflow

```text
Game event CSV
      |
      v
Load and validate input columns
      |
      v
Data cleaning and quality checks
      |
      v
Clean event data
      |
      +----------------------+
      |                      |
      v                      v
Pandas KPI calculations   SQLite events table
      |                      |
      |                      v
      |                  SQL KPI calculations
      |                      |
      +----------+-----------+
                 |
                 v
       Compare SQL and Pandas
                 |
                 v
       Dashboard, cohorts and report
```

## 6. Dataset Format

Upload a CSV containing these five required columns:

| Column | Description | Example |
|---|---|---|
| `event_id` | Unique event identifier | `E000001` |
| `player_id` | Player identifier | `P0001` |
| `event_type` | Type of event | `session_start` |
| `event_timestamp` | Event date and time | `2026-10-01T10:30:00Z` |
| `revenue` | Revenue associated with the event | `0.00` or `4.99` |

Supported event types used by the sample analytics:
- `session_start`
- `app_open`
- `level_complete`
- `purchase`

The application treats `session_start`, `app_open`, `level_complete`, and `purchase` as qualifying activity events. Revenue is summed only for `purchase` events.

**Sample data:** The repository includes `data/game_events.csv`, a synthetic dataset for local testing. It does not represent real users or real commercial performance.

## 7. Metric Definitions and Assumptions

The application uses the following explicit definitions:

| Metric | Definition |
|---|---|
| Active users | Distinct players with at least one qualifying activity event in the selected dataset |
| Purchase revenue | Sum of `revenue` for rows where `event_type = purchase` |
| Paying users | Distinct players with at least one purchase event where revenue is greater than zero |
| ARPU | Purchase revenue / active users |
| ARPPU | Purchase revenue / paying users |
| D1 retention | Percentage of a cohort active exactly one calendar day after its first active date |
| D7 retention | Percentage of a cohort active exactly seven calendar days after its first active date |
| D30 retention | Percentage of a cohort active exactly thirty calendar days after its first active date |

**Important interpretation notes:**
- Retention uses an exact calendar-day return definition, not a rolling 24-hour window.
- Recent cohorts may not yet have a complete D7 or D30 observation window. A missing future observation should not be interpreted as confirmed churn.
- ARPU and ARPPU are calculated over the uploaded dataset's full date range, not a selectable reporting window.
- The current dashboard reports descriptive patterns. It does not establish the cause of a revenue or retention change.

## 8. Run Locally

### Prerequisites
- Python 3.10 or newer recommended.
- Git (optional, for cloning the repository).

### Clone the repository

```bash
git clone https://github.com/OM-2204/Game-Analytics-Dashboard
cd game-analytics-agent
```

Replace `https://github.com/OM-2204/Game-Analytics-Dashboard` with your actual public GitHub repository URL.

### Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start the application

```bash
streamlit run app.py
```

Streamlit will print a local URL, usually `http://localhost:8501`.

## 9. Run the Tests

Run the automated test suite from the project root:

```bash
pytest -v
```

The tests cover examples of:
- KPI calculations.
- Exact calendar-day D1 retention.
- Detection of invalid and duplicate records.
- SQL/Pandas KPI reconciliation.

The test fixtures contain small, manually understandable examples so expected values can be checked independently.

## 10. Repository Structure

```text
game-analytics-agent/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   ├── game_events.csv
│   └── game_events_dirty_sample.csv
│
├── src/
│   ├── __init__.py
│   ├── data_processing.py
│   ├── analytics.py
│   ├── validation.py
│   └── report_generator.py
│
├── tests/
│   ├── conftest.py
│   ├── test_analytics.py
│   └── test_validation.py
│
└── reports/
```

Generated SQLite database files and generated reports are excluded from version control by `.gitignore`.

## 11. How the Project Demonstrates AI-Assisted Development

ChatGPT was used as a development assistant to help plan the project structure, draft implementation code, explain logic, troubleshoot issues, and create test cases.

The project is designed around a key principle: **AI-generated code and analytical outputs should be inspected and tested rather than accepted blindly.**

Evidence of validation in this implementation includes:
1. Separate Pandas and SQL implementations for headline KPIs.
2. Reconciliation checks that compare their outputs.
3. Unit tests with expected values.
4. Deliberately malformed sample records to exercise data-quality checks.

When presenting this project, explain which parts were AI-assisted, what you reviewed or changed, what tests you ran, and what the tests do and do not prove. Do not claim that the application uses an autonomous LLM agent to generate SQL: the current version uses predefined, deterministic analytics and validation logic.

## 12. Current Limitations and Future Improvements

### Current limitations
- Uses synthetic demonstration data; no real game telemetry integration.
- Does not currently generate SQL from natural-language questions.
- Does not use an LLM to infer the cause of metric changes.
- Does not currently include A/B-test analysis, acquisition attribution, or monetization-funnel analysis.
- SQL/Pandas reconciliation checks implementation consistency for selected KPIs, not the correctness of every chart or metric.
- Data-quality rules are basic and may need to be adapted for a real game's event schema.

### Planned improvements
- Natural-language question answering for analytics questions.
- Guarded AI-generated SQL with read-only execution, query validation, and result checks.
- Player segmentation and retention investigation.
- A/B-test and experiment analysis.
- Automated scheduled reporting.
- More comprehensive data contracts and tests.

## 13. Author

**Om Prakash Mallick**

B.Tech, Mining Engineering  
National Institute of Technology, Rourkela

---

If you find an issue or have a suggestion, feel free to open an issue in the repository.

**[View the live application](https://game-analytics-dashboard-lydumca8dkja46wmdtjgef.streamlit.app/)**
