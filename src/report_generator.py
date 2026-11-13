from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

def build_markdown_report(kpis: dict, daily: pd.DataFrame, validation: dict, quality: dict) -> str:
    if daily.empty:
        trend = "No daily activity data available."
    else:
        first = float(daily.iloc[0]["Revenue"])
        last = float(daily.iloc[-1]["Revenue"])
        if first == 0:
            trend = f"Revenue on the first date was ₹{first:,.2f}; latest date revenue was ₹{last:,.2f}. Percentage change is not calculated when the first date is zero."
        else:
            change = (last - first) / first * 100
            trend = f"Revenue changed by {change:.1f}% from the first to the last date in the selected dataset."
    status = "PASS" if validation["passed"] else "FAIL"
    return f"""# Game Analytics Summary

Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}

## Key metrics
- Active users in selected dataset: {kpis['active_users']:,}
- Purchase revenue: ₹{kpis['total_revenue']:,.2f}
- Paying users: {kpis['paying_users']:,}
- ARPU (revenue / active users): ₹{kpis['arpu']:,.2f}
- ARPPU (revenue / paying users): ₹{kpis['arppu']:,.2f}

## Observation
{trend}

## Data quality
- Raw rows: {quality['raw_rows']:,}
- Clean rows used: {quality['clean_rows']:,}
- Excluded / duplicate rows: {quality['excluded_or_duplicate_rows']:,}
- Issues flagged: {quality['issues_found']:,}

## Independent validation
- SQL vs Pandas reconciliation: **{status}**
- Individual checks: {validation['checks']}

## Interpretation note
These metrics describe the supplied dataset only. They do not establish why a metric changed; further segmentation and investigation are required before making causal claims.
"""

def save_report(report: str, path: str = "reports/latest_report.md") -> str:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    return str(output)
