import pandas as pd
import numpy as np
from typing import Dict, Any

class SharedAnalysisEngine:
    """Universal Company Health & Data Integrity Analysis Library."""

    def analyze_universal_health(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Computes cross-industry health indicators across financial, operational, and data governance dimensions."""
        health_summary = {
            "data_integrity": self._analyze_data_integrity(df),
            "financial_health": self._analyze_financial_health(df),
            "operational_volatility": self._analyze_volatility(df)
        }
        return health_summary

    def _analyze_data_integrity(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Evaluates baseline data completeness and duplicate rates."""
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()
        completeness_pct = round(((total_cells - missing_cells) / total_cells) * 100, 2) if total_cells > 0 else 100.0
        
        duplicate_rows = df.duplicated().sum()
        duplicate_pct = round((duplicate_rows / len(df)) * 100, 2) if len(df) > 0 else 0.0

        return {
            "completeness_score_pct": completeness_pct,
            "duplicate_rows_count": int(duplicate_rows),
            "duplicate_rate_pct": duplicate_pct,
            "total_records": len(df),
            "total_columns": len(df.columns)
        }

    def _analyze_financial_health(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Dynamically computes financial ratios if cost/revenue metrics exist in the schema."""
        rev_col = next((c for c in df.columns if any(k in c.lower() for k in ['revenue', 'sales', 'billedamount', 'grossrevenue'])), None)
        cost_col = next((c for c in df.columns if any(k in c.lower() for k in ['cost', 'expenses', 'opex', 'tripcost'])), None)

        financials = {"financial_metrics_found": False}

        if rev_col and pd.api.types.is_numeric_dtype(df[rev_col]):
            total_rev = df[rev_col].sum()
            financials["total_revenue"] = round(float(total_rev), 2)
            financials["avg_revenue_per_record"] = round(float(df[rev_col].mean()), 2)
            financials["financial_metrics_found"] = True

        if cost_col and pd.api.types.is_numeric_dtype(df[cost_col]):
            total_cost = df[cost_col].sum()
            financials["total_cost"] = round(float(total_cost), 2)
            financials["avg_cost_per_record"] = round(float(df[cost_col].mean()), 2)
            financials["financial_metrics_found"] = True

        if rev_col and cost_col and financials["financial_metrics_found"]:
            total_rev = financials.get("total_revenue", 0)
            total_cost = financials.get("total_cost", 0)
            if total_rev > 0:
                profit_margin = ((total_rev - total_cost) / total_rev) * 100
                financials["estimated_profit_margin_pct"] = round(float(profit_margin), 2)
                financials["expense_ratio"] = round(float(total_cost / total_rev), 2)

        return financials

    def _analyze_volatility(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates process stability via Coefficient of Variation (Std/Mean) across numeric indicators."""
        numeric_cols = df.select_dtypes(include=['number']).columns
        volatility_scores = {}

        for col in numeric_cols:
            mean_val = df[col].mean()
            std_val = df[col].std()
            if mean_val and mean_val != 0 and not np.isnan(std_val):
                cv = (std_val / abs(mean_val))
                volatility_scores[col] = {
                    "coefficient_of_variation": round(float(cv), 2),
                    "stability_status": "High Volatility" if cv > 0.5 else "Stable"
                }

        return {
            "volatility_by_metric": volatility_scores
        }
