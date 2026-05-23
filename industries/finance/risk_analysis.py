"""Risk KPIs: credit/default metrics and concentration risk."""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_risk_metrics(df):
    kpis = []
    loan_id = first_column(df, ["loan_id", "loan_account", "credit_id"]) 
    default_flag = first_column(df, ["default_flag", "is_default", "defaulted"]) 
    balance = first_column(df, ["balance", "outstanding"])

    if not loan_id and not default_flag:
        return kpis

    conf, warns = evaluate_kpi_confidence(df, [loan_id, default_flag, balance])

    if default_flag:
        defaults = int(df[default_flag].astype(bool).sum())
        total = len(df)
        rate = defaults / total if total > 0 else 0
        kpis.append({
            "category": "🛡️ Risk",
            "name": "Default Rate",
            "value": f"{rate:.2%}",
            "formula": "Count(Default) / Count(Records)",
            "source": f"`{default_flag}`",
            "confidence": conf,
            "warnings": warns,
        })

    if balance and default_flag:
        npl = df[df[default_flag].astype(bool)][balance].sum()
        tot_bal = df[balance].sum() if df[balance].sum() != 0 else 1
        npl_ratio = npl / tot_bal
        kpis.append({
            "category": "🛡️ Risk",
            "name": "Non-Performing Loan Ratio",
            "value": f"{npl_ratio:.2%}",
            "formula": "NPL / Total Balance",
            "source": f"`{balance}`, `{default_flag}`",
            "confidence": conf,
            "warnings": warns,
        })

    return kpis
