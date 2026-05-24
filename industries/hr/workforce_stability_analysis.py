import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_workforce_stability_metrics(df):
    kpis = []
    if len(df) == 0:
        return kpis

    # Aliases
    attrition_col = first_column(df, ["Attrition", "attrition", "left_company", "status", "voluntary_leave"])
    tenure_col = first_column(df, ["YearsAtCompany", "yearsatcompany", "tenure", "length_of_service"])
    role_tenure_col = first_column(df, ["YearsInCurrentRole", "yearsincurrentrole", "role_tenure"])
    manager_tenure_col = first_column(df, ["YearsWithCurrManager", "yearswithcurrmanager", "manager_tenure"])

    # 🛑 The only kill-switch left is Attrition itself. If no attrition column exists, skip attrition math.
    if not attrition_col and not tenure_col:
        return kpis

    conf, warns = confidence_for(df, [col for col in [attrition_col, tenure_col, role_tenure_col] if col])

    if attrition_col:
        attrition_series = df[attrition_col].astype(str).str.lower()
        left_count = attrition_series.isin(["yes", "true", "1", "left", "terminated"]).sum()
        total_employees = len(df)
        attrition_rate = (left_count / total_employees * 100) if total_employees > 0 else 0

        kpis.append(safe_kpi(
            category="📉 Retention Analytics", name="Overall Attrition Rate",
            value=f"{attrition_rate:.1f}%", formula="(Employees Left / Total) * 100",
            source=f"`{attrition_col}`", confidence=conf,
            warnings="High attrition detected (>15%)" if attrition_rate > 15 else warns
        ))

    if tenure_col and pd.api.types.is_numeric_dtype(df[tenure_col]):
        avg_tenure = df[tenure_col].dropna().mean()
        kpis.append(safe_kpi(
            category="📉 Retention Analytics", name="Avg Company Tenure",
            value=f"{avg_tenure:.1f} Years", formula="Mean(YearsAtCompany)",
            source=f"`{tenure_col}`", confidence=conf, warnings=warns
        ))

    if role_tenure_col and pd.api.types.is_numeric_dtype(df[role_tenure_col]):
        avg_role_tenure = df[role_tenure_col].dropna().mean()
        kpis.append(safe_kpi(
            category="📉 Retention Analytics", name="Avg Time in Current Role",
            value=f"{avg_role_tenure:.1f} Years", formula="Mean(YearsInCurrentRole)",
            source=f"`{role_tenure_col}`", confidence=conf,
            warnings="High role stagnation (>4 years)" if avg_role_tenure > 4 else warns
        ))

    return kpis
