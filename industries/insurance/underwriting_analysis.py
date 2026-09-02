"""
Underwriting profitability KPIs: loss ratio, combined ratio, premium adequacy.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

INSURANCE_CONFIG = {
    "missing_data_threshold": 5,
    "score_deduction_for_warning": 20,
    "low_confidence_threshold": 25,
}


def calc_underwriting_metrics(df, enable_debug=False):
    """
    Loss Ratio = Incurred Losses / Earned Premiums
    Combined Ratio = (Incurred Losses + Underwriting Expenses) / Earned Premiums
    """
    engine = KPIEngine(df, industry_config=INSURANCE_CONFIG)
    if enable_debug:
        engine.enable_tracing()

    kpis = []
    if len(df) == 0:
        return kpis

    premium_col, premium_series = engine.get_numeric(["premium_amount", "annual_premium", "premium_paid", "gross_premium"])
    loss_col, loss_series = engine.get_numeric(["incurred_loss", "incurred_losses", "loss_amount", "total_incurred"])
    expense_col, expense_series = engine.get_numeric(["expense", "underwriting_expense", "opex"])

    if premium_col is not None:
        total_premium = premium_series.fillna(0).sum()
        kpis.append(engine.build_kpi(
            category="📋 Underwriting", name="Total Earned Premium",
            value=f"${total_premium:,.2f}", formula="Sum(Premium)", source=f"`{premium_col}`"
        ))
    else:
        kpis.append(engine.log_missing("📋 Underwriting", "Total Earned Premium", "Missing numeric 'premium' column."))

    if premium_col is not None and loss_col is not None:
        total_loss = loss_series.fillna(0).sum()
        total_premium = premium_series.fillna(0).sum()
        loss_ratio = (total_loss / total_premium * 100) if total_premium > 0 else 0
        kpis.append(engine.build_kpi(
            category="📋 Underwriting", name="Loss Ratio",
            value=f"{loss_ratio:.2f}%", formula="Incurred Losses / Earned Premiums * 100",
            source=f"`{loss_col}`, `{premium_col}`"
        ))

        if expense_col is not None:
            total_expense = expense_series.fillna(0).sum()
            combined_ratio = ((total_loss + total_expense) / total_premium * 100) if total_premium > 0 else 0
            kpis.append(engine.build_kpi(
                category="📋 Underwriting", name="Combined Ratio",
                value=f"{combined_ratio:.2f}%",
                formula="(Incurred Losses + Underwriting Expenses) / Earned Premiums * 100",
                source=f"`{loss_col}`, `{expense_col}`, `{premium_col}`"
            ))
        else:
            kpis.append(engine.log_missing("📋 Underwriting", "Combined Ratio", "Missing numeric 'expense' column."))
    else:
        kpis.append(engine.log_missing("📋 Underwriting", "Loss Ratio", "Missing 'premium' and/or 'incurred_loss' columns."))

    if enable_debug:
        engine.print_execution_log()

    return kpis
