"""Revenue KPIs: totals, growth and average ticket."""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_fore
from utils.validator import SemanticValidator

def calc_revenue_metrics(df):
    kpis = []
    revenue_col = first_column(df, ["revenue", "sales", "turnover"])
    date_col = first_column(df, ["date", "transaction_date", "period"])
    ticket_col = first_column(df, ["ticket_value", "amount", "value"])

    if not revenue_col:
        return kpis

    conf, warns = evaluate_kpi_confidence(df, [revenue_col, date_col, ticket_col])
    total_revenue = df[revenue_col].sum()

    kpis.append({
        "category": "📣 Revenue",
        "name": "Total Revenue",
        "value": f"${total_revenue:,.2f}",
        "formula": "Sum(Revenue)",
        "source": f"`{revenue_col}`",
        "confidence": conf,
        "warnings": warns,
    })

    if ticket_col:
        avg_ticket = df[ticket_col].mean()
        kpis.append({
            "category": "📣 Revenue",
            "name": "Avg Ticket Value",
            "value": f"${avg_ticket:,.2f}",
            "formula": "Mean(Ticket Value)",
            "source": f"`{ticket_col}`",
            "confidence": conf,
            "warnings": warns,
        })

    if date_col:
        try:
            df_date = df.copy()
            df_date["_d"] = pd.to_datetime(df_date[date_col], errors="coerce")
            df_month = df_date.dropna(subset=["_d"]).set_index("_d").resample('M')[revenue_col].sum()
            if len(df_month) >= 2:
                growth = df_month.pct_change().dropna().mean()
                kpis.append({
                    "category": "📣 Revenue",
                    "name": "Avg Monthly Revenue Growth",
                    "value": f"{growth:.2%}",
                    "formula": "Mean(Monthly % Change)",
                    "source": f"`{date_col}`, `{revenue_col}`",
                    "confidence": conf,
                    "warnings": warns,
                })
        except Exception:
            pass

    return kpis
