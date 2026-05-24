"""
Recruitment efficiency, hiring pipeline, and talent acquisition metrics.
GOVERNANCE: Process metrics ONLY - No candidate personality assessment.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_recruitment_metrics(df):
    """Calculates recruitment and hiring pipeline KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Recruitment metrics are COUNT (candidates, positions), not time
    candidate_col = first_column(df, ["candidate_id", "applicant_id", "hire_id"])
    position_col = first_column(df, ["position_id", "job_id", "requisition_id"])
    status_col = first_column(df, ["status", "hiring_status", "process_status"])
    hired_col = first_column(df, ["hired", "offer_accepted", "hired_flag"])
    # Time-to-hire is ELAPSED TIME (days from application to hire)
    tth_col = first_column(df, ["time_to_hire_days", "days_to_hire", "hiring_duration"])
    application_date_col = first_column(df, ["application_date", "application_submitted"])
    hire_date_col = first_column(df, ["hire_date", "start_date", "offer_date"])
    cost_col = first_column(df, ["recruitment_cost", "hiring_cost", "acquisition_cost"])
    
    if not candidate_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [candidate_col, position_col, status_col, tth_col, cost_col] if col])
    
    # Total candidates
    total_candidates = df[candidate_col].nunique()
    
    kpis.append(safe_kpi(
        category="🎯 Recruitment",
        name="Total Candidates",
        value=f"{total_candidates:,}",
        formula="Count(Distinct Candidates)",
        source=f"`{candidate_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Hiring outcomes
    if hired_col:
        hired_mask = df[hired_col].astype(str).str.lower().isin(['1', 'true', 'yes', 'hired'])
        hired_count = hired_mask.sum()
        offer_acceptance_rate = (hired_count / total_candidates * 100) if total_candidates > 0 else 0
        
        kpis.append(safe_kpi(
            category="🎯 Recruitment",
            name="Total Hires",
            value=f"{hired_count:,}",
            formula="Count(Hired = True)",
            source=f"`{hired_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="🎯 Recruitment",
            name="Offer Acceptance Rate",
            value=f"{offer_acceptance_rate:.2f}%",
            formula="(Hired / Total Candidates) * 100",
            source=f"`{hired_col}`",
            confidence=conf,
            warnings="Low acceptance rate (<50%)" if offer_acceptance_rate < 50 else warns
        ))
    
    # Open positions
    if position_col:
        total_positions = df[position_col].nunique()
        
        kpis.append(safe_kpi(
            category="🎯 Recruitment",
            name="Total Open Positions",
            value=f"{total_positions}",
            formula="Count(Distinct Positions)",
            source=f"`{position_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        # Vacancy fill rate
        if hired_col:
            filled_positions = df[hired_mask][position_col].nunique()
            fill_rate = (filled_positions / total_positions * 100) if total_positions > 0 else 0
            
            kpis.append(safe_kpi(
                category="🎯 Recruitment",
                name="Position Fill Rate",
                value=f"{fill_rate:.2f}%",
                formula="(Filled Positions / Open Positions) * 100",
                source=f"`{position_col}`, `{hired_col}`",
                confidence=conf,
                warnings="High vacancy rate (<70%)" if fill_rate < 70 else warns
            ))
    
    # Time-to-hire (⏱️ ELAPSED TIME - days from application to offer/hire)
    if tth_col:
        is_valid, reason = SemanticValidator.is_valid_duration(df[tth_col])
        
        if is_valid and pd.api.types.is_numeric_dtype(df[tth_col]):
            valid_tth = df[tth_col].dropna()
            
            if not valid_tth.empty:
                avg_tth = valid_tth.mean()
                median_tth = valid_tth.median()
                max_tth = valid_tth.max()
                
                kpis.append(safe_kpi(
                    category="⏱️ Hiring Timeline",
                    name="Avg Time-to-Hire",
                    value=f"{avg_tth:.0f} days",
                    formula="Mean(Days from Application to Hire)",
                    source=f"`{tth_col}`",
                    confidence=conf,
                    warnings="Long hiring process (>60 days)" if avg_tth > 60 else warns
                ))
                
                kpis.append(safe_kpi(
                    category="⏱️ Hiring Timeline",
                    name="Median Time-to-Hire",
                    value=f"{median_tth:.0f} days",
                    formula="Median(Days from Application to Hire)",
                    source=f"`{tth_col}`",
                    confidence=conf,
                    warnings=warns
                ))
                
                kpis.append(safe_kpi(
                    category="⏱️ Hiring Timeline",
                    name="Max Time-to-Hire",
                    value=f"{max_tth:.0f} days",
                    formula="Max(Days from Application to Hire)",
                    source=f"`{tth_col}`",
                    confidence=conf,
                    warnings="Critical delay in hiring" if max_tth > 120 else warns
                ))
        else:
            kpis.append(safe_kpi(
                category="⏱️ Hiring Timeline",
                name="Time-to-Hire Metrics",
                value="EXCLUDED",
                formula="N/A",
                source=f"`{tth_col}`",
                confidence="Low",
                warnings=f"Invalid duration: {reason}"
            ))
    
    # Alternative: Calculate from dates (⏱️ EXACT DATES)
    if application_date_col and hire_date_col and not tth_col:
        app_dt = pd.to_datetime(df[application_date_col], errors="coerce")
        hire_dt = pd.to_datetime(df[hire_date_col], errors="coerce")
        
        app_valid, app_reason = SemanticValidator.is_valid_datetime(app_dt.dropna())
        hire_valid, hire_reason = SemanticValidator.is_valid_datetime(hire_dt.dropna())
        
        if app_valid and hire_valid:
            date_df = pd.DataFrame({
                "app_date": app_dt,
                "hire_date": hire_dt
            }).dropna()
            
            if not date_df.empty:
                date_df["tth_days"] = (date_df["hire_date"] - date_df["app_date"]).dt.total_seconds() / 86400
                valid_tth = date_df["tth_days"].dropna()
                
                if not valid_tth.empty:
                    kpis.append(safe_kpi(
                        category="⏱️ Hiring Timeline",
                        name="Avg Time-to-Hire (Calculated)",
                        value=f"{valid_tth.mean():.0f} days",
                        formula="Mean(Hire Date - Application Date)",
                        source=f"`{application_date_col}`, `{hire_date_col}`",
                        confidence=conf,
                        warnings="Long hiring process (>60 days)" if valid_tth.mean() > 60 else warns
                    ))
    
    # Recruitment cost
    if cost_col and pd.api.types.is_numeric_dtype(df[cost_col]):
        total_cost = df[cost_col].sum()
        cost_per_hire = (total_cost / hired_count) if hired_col and hired_count > 0 else 0
        
        kpis.append(safe_kpi(
            category="💰 Recruitment Cost",
            name="Total Recruitment Cost",
            value=f"${total_cost:,.2f}",
            formula="Sum(Recruitment Cost)",
            source=f"`{cost_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        if hired_count > 0:
            kpis.append(safe_kpi(
                category="💰 Recruitment Cost",
                name="Cost per Hire",
                value=f"${cost_per_hire:,.2f}",
                formula="Total Cost / Hires",
                source=f"`{cost_col}`, `{hired_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    return kpis
