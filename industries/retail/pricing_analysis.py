import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def calc_pricing_metrics(df):
    """Calculates pricing, markdown, and margin pressure KPIs."""
    kpis = []
    discount_col = _first_column(df, ["discount_pct", "discount", "markdown_pct"])
    revenue_col = _first_column(df, ["revenue", "sales", "weekly_sales", "total_sales"])
    margin_col = _first_column(df, ["margin", "gross_margin", "profit_margin"])
    markdown_flag_col = _first_column(df, ["is_markdown", "markdown_flag"])

    if not discount_col and not margin_col:
        return kpis

    columns_for_conf = [c for c in [discount_col, revenue_col, margin_col, markdown_flag_col] if c]
    conf, warns = evaluate_kpi_confidence(df, columns_for_conf)

    if discount_col:
        disc_valid, reason = SemanticValidator.is_valid_percentage(df[discount_col].fillna(0))
        if disc_valid:
            avg_discount = df[discount_col].dropna().mean()
            kpis.append({
                "category": "🏷️ Pricing Analysis",
                "name": "Avg Discount %",
                "value": f"{avg_discount:.2f}%",
                "formula": "Mean(Discount %)",
                "source": f"`{discount_col}`",
                "confidence": conf,
                "warnings": warns,
            })

            if revenue_col:
                discounted_revenue = df.loc[df[discount_col].fillna(0) > 0, revenue_col].sum()
                total_revenue = df[revenue_col].sum()
                discounted_share = (discounted_revenue / total_revenue * 100) if total_revenue > 0 else 0
                markdown_frequency = (df[discount_col].fillna(0) > 0).mean() * 100
                kpis.append({
                    "category": "🏷️ Pricing Analysis",
                    "name": "Discounted Sales Share",
                    "value": f"{discounted_share:.2f}%",
                    "formula": "Discounted Revenue / Total Revenue * 100",
                    "source": f"`{discount_col}`, `{revenue_col}`",
                    "confidence": conf,
                    "warnings": warns,
                })
                kpis.append({
                    "category": "🏷️ Pricing Analysis",
                    "name": "Markdown Frequency",
                    "value": f"{markdown_frequency:.2f}%",
                    "formula": "Rows with discount > 0 / Total rows * 100",
                    "source": f"`{discount_col}`",
                    "confidence": conf,
                    "warnings": warns,
                })
        else:
            kpis.append({
                "category": "🏷️ Pricing Analysis",
                "name": "Pricing Metrics",
                "value": "EXCLUDED",
                "formula": "N/A",
                "source": f"`{discount_col}`",
                "confidence": "Low",
                "warnings": reason,
            })

    if margin_col:
        margin_valid, reason = SemanticValidator.is_valid_percentage(df[margin_col].fillna(0))
        if margin_valid:
            margin_compression = df[margin_col].dropna().diff().mean() * -1
            kpis.append({
                "category": "🏷️ Pricing Analysis",
                "name": "Margin Compression",
                "value": f"{margin_compression:.2f} pp",
                "formula": "-Mean(Diff(Margin %))",
                "source": f"`{margin_col}`",
                "confidence": conf,
                "warnings": warns,
            })
        else:
            kpis.append({
                "category": "🏷️ Pricing Analysis",
                "name": "Margin Compression",
                "value": "EXCLUDED",
                "formula": "N/A",
                "source": f"`{margin_col}`",
                "confidence": "Low",
                "warnings": reason,
            })

    if markdown_flag_col:
        markdown_series = df[markdown_flag_col].astype(str).str.lower().isin(["true", "1", "yes", "y"])
        kpis.append({
            "category": "🏷️ Pricing Analysis",
            "name": "Markdown Frequency",
            "value": f"{(markdown_series.mean() * 100):.2f}%",
            "formula": "Markdown rows / Total rows * 100",
            "source": f"`{markdown_flag_col}`",
            "confidence": conf,
            "warnings": warns,
        })

    return kpis
