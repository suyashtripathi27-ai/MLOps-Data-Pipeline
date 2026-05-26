"""
Recruitment efficiency, hiring pipeline, and talent acquisition metrics.
GOVERNANCE: Process metrics ONLY - No candidate personality assessment.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine
from utils.validator import SemanticValidator

# HR Industry Configuration
HR_CONFIG = {
    "missing_data_threshold": 12,
    "score_deduction_for_warning": 10,
    "low_confidence_threshold": 40,
}

def calc_recruitment_metrics(df, enable_debug=False):
    """Calculates recruitment and hiring pipeline KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Initialize engine with HR config
    engine = KPIEngine(df, industry_config=HR_CONFIG)
    if enable_debug:
        engine.enable_tracing()
    
    # Recruitment metrics are COUNT (candidates, positions), not time
    candidate_col, candidate_series = engine.get_column(["candidate_id", "applicant_id", "hire_id"])
    position_col, position_series = engine.get_column(["position_id", "job_id", "requisition_id"])
    status_col, status_series = engine.get_column(["status", "hiring_status", "process_status"])
    hired_col, hired_series = engine.get_column(["hired", "offer_accepted", "hired_flag"])
    # Time-to-hire is ELAPSED TIME (days from application to hire)
    tth_col, tth_series = engine.get_numeric(["time_to_hire_days", "days_to_hire", "hiring_duration"])
    application_date_col, application_date_series = engine.get_column(["application_date", "application_submitted"])
    hire_date_col, hire_date_series = engine.get_column(["hire_date", "start_date", "offer_date"])
    cost_col, cost_series = engine.get_numeric(["recruitment_cost", "cost_per_hire", "hiring_cost"])
    
    if not candidate_col:
        return kpis
    
    # Total candidates
    total_candidates = candidate_series.nunique()
    
    kpis.append(engine.build_kpi(
        category="👥 Recruitment",
        name="Total Candidates",
        value=f"{total_candidates:,}",
        formula="Count(Distinct Candidates)",
        source=f"`{candidate_col}`"
    ))
    
    # Positions
    if position_col:
        total_positions = position_series.nunique()
        
        kpis.append(engine.build_kpi(
            category="📋 Positions",
            name="Total Open Positions",
            value=f"{total_positions}",
            formula="Count(Distinct Positions)",
            source=f"`{position_col}`"
        ))
    
    # Hired count
    if hired_col:
        hired_mask = hired_series.astype(str).str.lower().isin(['1', 'true', 'yes', 'hired', 'accepted'])
        hired_count = hired_mask.sum()
        hiring_rate = (hired_count / len(df) * 100) if len(df) > 0 else 0
        
        kpis.append(engine.build_kpi(
            category="✅ Hires",
            name="Total Hired",
            value=f"{hired_count:,}",
            formula="Count(Hired = True)",
            source=f"`{hired_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="✅ Hires",
            name="Hiring Conversion Rate",
            value=f"{hiring_rate:.2f}%",
            formula="(Hired / Total Candidates) * 100",
            source=f"`{hired_col}`",
            warnings="Low conversion rate (<5%)" if hiring_rate < 5 else None
        ))
    
    # Time-to-hire (⏱️ ELAPSED TIME - days from application to offer/hire)
    if tth_col and not tth_series.empty:
        is_valid, reason = SemanticValidator.is_valid_duration(tth_series)
        
        if is_valid:
            valid_tth = tth_series.dropna()
            
            if not valid_tth.empty:
                avg_tth = valid_tth.mean()
                median_tth = valid_tth.median()
                max_tth = valid_tth.max()
                
                kpis.append(engine.build_kpi(
                    category="⏱️ Hiring Timeline",
                    name="Avg Time-to-Hire",
                    value=f"{avg_tth:.0f} days",
                    formula="Mean(Days from Application to Hire)",
                    source=f"`{tth_col}`",
                    warnings="Long hiring process (>60 days)" if avg_tth > 60 else None
                ))
                
                kpis.append(engine.build_kpi(
                    category="⏱️ Hiring Timeline",
                    name="Median Time-to-Hire",
                    value=f"{median_tth:.0f} days",
                    formula="Median(Days from Application to Hire)",
                    source=f"`{tth_col}`"
                ))
                
                kpis.append(engine.build_kpi(
                    category="⏱️ Hiring Timeline",
                    name="Max Time-to-Hire",
                    value=f"{max_tth:.0f} days",
                    formula="Max(Days from Application to Hire)",
                    source=f"`{tth_col}`",
                    warnings="Critical delay in hiring (>120 days)" if max_tth > 120 else None
                ))
    
    # Calculate TTH from dates if direct column not available
    if application_date_col and hire_date_col:
        try:
            date_df = pd.DataFrame({
                "app_date": pd.to_datetime(application_date_series, errors='coerce'),
                "hire_date": pd.to_datetime(hire_date_series, errors='coerce')
            })
            date_df["tth_days"] = (date_df["hire_date"] - date_df["app_date"]).dt.days
            valid_tth = date_df["tth_days"].dropna()
            
            if not valid_tth.empty:
                kpis.append(engine.build_kpi(
                    category="⏱️ Hiring Timeline",
                    name="Avg Time-to-Hire (Calculated)",
                    value=f"{valid_tth.mean():.0f} days",
                    formula="Mean(Hire Date - Application Date)",
                    source=f"`{application_date_col}`, `{hire_date_col}`",
                    warnings="Long hiring process (>60 days)" if valid_tth.mean() > 60 else None
                ))
        except Exception as e:
            pass
    
    # Recruitment cost
    if cost_col and not cost_series.empty:
        total_cost = cost_series.sum()
        cost_per_hire = (total_cost / hired_count) if hired_col and hired_count > 0 else 0
        
        kpis.append(engine.build_kpi(
            category="💰 Recruitment Cost",
            name="Total Recruitment Cost",
            value=f"${total_cost:,.2f}",
            formula="Sum(Recruitment Cost)",
            source=f"`{cost_col}`"
        ))
        
        if hired_count > 0:
            kpis.append(engine.build_kpi(
                category="💰 Recruitment Cost",
                name="Cost per Hire",
                value=f"${cost_per_hire:,.2f}",
                formula="Total Cost / Hires",
                source=f"`{cost_col}`"
            ))
    
    return kpis
