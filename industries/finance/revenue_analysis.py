"""
Revenue streams, growth, and sales metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

FINANCE_CONFIG = {
    "missing_data_threshold": 3,
    "score_deduction_for_warning": 20,
    "low_confidence_threshold": 50,
}

def calc_revenue_metrics(df, enable_debug=False):
    engine = KPIEngine(df, industry_config=FINANCE_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    kpis = []
    if len(df) == 0: return kpis
    
    revenue_col, revenue_series = engine.get_numeric(["revenue", "sales", "gross_revenue", "income", "turnover"])
    date_col, date_series = engine.get_datetime(["date", "transaction_date", "report_date", "period"])
    segment_col, segment_series = engine.get_column(["revenue_segment", "business_segment", "category", "division"])
    
    if revenue_col is None:
        kpis.append(engine.log_missing("📈 Revenue", "Revenue Metrics", "Missing numeric 'revenue'."))
        return kpis
    
    total_revenue = revenue_series.sum()
    kpis.append(engine.build_kpi(
        category="📈 Revenue", name="Total Revenue",
        value=f"${total_revenue:,.2f}", formula="Sum(Revenue)", source=f"`{revenue_col}`"
    ))
    kpis.append(engine.build_kpi(
        category="📈 Revenue", name="Avg Revenue",
        value=f"${revenue_series.mean():,.2f}", formula="Mean(Revenue)", source=f"`{revenue_col}`"
    ))
    kpis.append(engine.build_kpi(
        category="📈 Revenue", name="Median Revenue",
        value=f"${revenue_series.median():,.2f}", formula="Median(Revenue)", source=f"`{revenue_col}`"
    ))
    
    if date_col is not None:
        df_temp = pd.concat([date_series, revenue_series], axis=1).dropna()
        if len(df_temp) > 1:
            df_temp["period"] = df_temp[date_col].dt.to_period("M")
            monthly = df_temp.groupby("period")[revenue_col].sum()
            if len(monthly) > 1:
                first_period = monthly.iloc[0]
                last_period = monthly.iloc[-1]
                growth = ((last_period - first_period) / first_period * 100) if first_period != 0 else 0
                warn_msg = "Negative growth - revenue decline" if growth < 0 else "Slow growth (<5%)" if growth < 5 else "None"
                kpis.append(engine.build_kpi(
                    category="📈 Revenue", name="Revenue Growth %",
                    value=f"{growth:.2f}%", formula="((Last Period - First) / First) * 100", 
                    source=f"`{revenue_col}`, `{date_col}`", warnings=warn_msg
                ))
    else:
        kpis.append(engine.log_missing("📈 Revenue", "Revenue Growth", "Missing valid 'date' column."))
    
    if segment_col is not None:
        revenue_by_seg = df.groupby(segment_col)[revenue_col].sum().sort_values(ascending=False)
        if len(revenue_by_seg) > 0:
            top_segment = revenue_by_seg.idxmax()
            top_segment_rev = revenue_by_seg.max()
            top_segment_share = (top_segment_rev / total_revenue * 100) if total_revenue > 0 else 0
            kpis.append(engine.build_kpi(
                category="📈 Revenue", name="Top Revenue Segment",
                value=f"{top_segment} (${top_segment_rev:,.2f})", formula="Segment with max revenue", 
                source=f"`{segment_col}`, `{revenue_col}`"
            ))
            kpis.append(engine.build_kpi(
                category="📈 Revenue", name="Top Segment Share %",
                value=f"{top_segment_share:.2f}%", formula="Top Segment / Total Revenue * 100", 
                source=f"`{segment_col}`, `{revenue_col}`", warnings="High concentration (>70%)" if top_segment_share > 70 else "None"
            ))
    else:
        kpis.append(engine.log_missing("📈 Revenue", "Revenue Segments", "Missing 'segment' column."))
    
    if enable_debug: engine.print_execution_log()
    return kpis
