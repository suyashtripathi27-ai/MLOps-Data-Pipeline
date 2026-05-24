"""
Risk metrics, exposure, and compliance analysis.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_risk_metrics(df):
    """Calculates risk and exposure KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    risk_score_col = first_column(df, ["risk_score", "exposure_score", "risk_rating"])
    loss_col = first_column(df, ["loss", "potential_loss", "expected_loss"])
    probability_col = first_column(df, ["probability", "default_probability", "risk_probability"])
    exposure_col = first_column(df, ["exposure", "at_risk", "credit_exposure", "market_exposure"])
    compliance_col = first_column(df, ["compliance_score", "compliance_status", "risk_compliant"])
    
    if not risk_score_col and not exposure_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [risk_score_col, loss_col, probability_col, exposure_col, compliance_col] if col])
    
    # Risk score analysis
    if risk_score_col and pd.api.types.is_numeric_dtype(df[risk_score_col]):
        valid_risk = df[risk_score_col].dropna()
        
        if not valid_risk.empty:
            avg_risk = valid_risk.mean()
            max_risk = valid_risk.max()
            
            kpis.append(safe_kpi(
                category="⚠️ Risk",
                name="Avg Risk Score",
                value=f"{avg_risk:.2f}",
                formula="Mean(Risk Score)",
                source=f"`{risk_score_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="⚠️ Risk",
                name="Max Risk Score",
                value=f"{max_risk:.2f}",
                formula="Max(Risk Score)",
                source=f"`{risk_score_col}`",
                confidence=conf,
                warnings="Critical risk detected" if max_risk > 80 else warns
            ))
            
            # High-risk items
            high_risk_threshold = valid_risk.quantile(0.75)
            high_risk_count = (valid_risk >= high_risk_threshold).sum()
            high_risk_pct = (high_risk_count / len(valid_risk) * 100) if len(valid_risk) > 0 else 0
            
            kpis.append(safe_kpi(
                category="⚠️ Risk",
                name="High-Risk Items (Top 25%)",
                value=f"{high_risk_count:,} ({high_risk_pct:.2f}%)",
                formula="Count(Risk >= 75th Percentile)",
                source=f"`{risk_score_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Expected loss
    if loss_col and pd.api.types.is_numeric_dtype(df[loss_col]):
        total_loss = df[loss_col].sum()
        avg_loss = df[loss_col].mean()
        
        kpis.append(safe_kpi(
            category="⚠️ Risk",
            name="Total Expected Loss",
            value=f"${total_loss:,.2f}",
            formula="Sum(Loss)",
            source=f"`{loss_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="⚠️ Risk",
            name="Avg Expected Loss",
            value=f"${avg_loss:,.2f}",
            formula="Mean(Loss)",
            source=f"`{loss_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Credit exposure
    if exposure_col and pd.api.types.is_numeric_dtype(df[exposure_col]):
        total_exposure = df[exposure_col].sum()
        
        kpis.append(safe_kpi(
            category="⚠️ Risk",
            name="Total Credit Exposure",
            value=f"${total_exposure:,.2f}",
            formula="Sum(Exposure)",
            source=f"`{exposure_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        # Concentration risk
        exposure_concentration = df[exposure_col].nlargest(3).sum()
        concentration_pct = (exposure_concentration / total_exposure * 100) if total_exposure > 0 else 0
        
        kpis.append(safe_kpi(
            category="⚠️ Risk",
            name="Top 3 Exposure Concentration",
            value=f"{concentration_pct:.2f}%",
            formula="(Top 3 / Total Exposure) * 100",
            source=f"`{exposure_col}`",
            confidence=conf,
            warnings="High concentration risk" if concentration_pct > 40 else warns
        ))
    
    # Compliance status
    if compliance_col:
        compliance_mask = df[compliance_col].astype(str).str.lower().isin(['1', 'true', 'yes', 'compliant'])
        compliant_count = compliance_mask.sum()
        compliant_pct = (compliant_count / len(df) * 100) if len(df) > 0 else 0
        
        kpis.append(safe_kpi(
            category="⚠️ Risk",
            name="Compliance Rate",
            value=f"{compliant_pct:.2f}%",
            formula="(Compliant / Total) * 100",
            source=f"`{compliance_col}`",
            confidence=conf,
            warnings="Low compliance rate" if compliant_pct < 80 else warns
        ))
    
    return kpis
