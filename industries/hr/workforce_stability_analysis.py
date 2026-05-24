"""
Workforce stability, attrition, turnover, and retention metrics.
GOVERNANCE: Operational metrics ONLY - No personality/intent inference.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_workforce_stability_metrics(df):
    """Calculates workforce stability and attrition KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Employee and status metrics are COUNT, not time
    employee_col = first_column(df, ["employee_id", "emp_id", "staff_id", "worker_id"])
    status_col = first_column(df, ["employment_status", "status", "current_status"])
    exit_col = first_column(df, ["exit_flag", "has_exited", "terminated", "left"])
    exit_type_col = first_column(df, ["exit_type", "separation_type", "exit_reason"])
    # Tenure is ELAPSED TIME (days/months employed)
    tenure_col = first_column(df, ["tenure_days", "tenure_months", "tenure_years", "employment_duration"])
    hire_date_col = first_column(df, ["hire_date", "start_date", "employment_date"])
    exit_date_col = first_column(df, ["exit_date", "termination_date", "last_date"])
    
    if not employee_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [employee_col, status_col, exit_col, tenure_col, hire_date_col, exit_date_col] if col])
    
    # Total headcount
    total_employees = df[employee_col].nunique()
    
    kpis.append(safe_kpi(
        category="👥 Workforce Stability",
        name="Total Active Employees",
        value=f"{total_employees:,}",
        formula="Count(Distinct Employees)",
        source=f"`{employee_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Attrition/turnover
    if exit_col:
        exit_mask = df[exit_col].astype(str).str.lower().isin(['1', 'true', 'yes', 'exited'])
        exits = exit_mask.sum()
        attrition_rate = (exits / total_employees * 100) if total_employees > 0 else 0
        
        kpis.append(safe_kpi(
            category="👥 Workforce Stability",
            name="Employee Exits/Attrition Count",
            value=f"{exits:,}",
            formula="Count(Exit Flag = True)",
            source=f"`{exit_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="👥 Workforce Stability",
            name="Attrition Rate",
            value=f"{attrition_rate:.2f}%",
            formula="(Exits / Total Employees) * 100",
            source=f"`{exit_col}`",
            confidence=conf,
            warnings="Critical attrition (>20%)" if attrition_rate > 20 else "High attrition (15-20%)" if attrition_rate > 15 else warns
        ))
    
    # Retention rate
    if status_col:
        active_mask = df[status_col].astype(str).str.lower().isin(['active', 'employed', 'current'])
        active_count = active_mask.sum()
        retention_rate = (active_count / total_employees * 100) if total_employees > 0 else 0
        
        kpis.append(safe_kpi(
            category="👥 Workforce Stability",
            name="Employee Retention Rate",
            value=f"{retention_rate:.2f}%",
            formula="(Active Employees / Total) * 100",
            source=f"`{status_col}`",
            confidence=conf,
            warnings="Low retention risk" if retention_rate < 80 else warns
        ))
    
    # Tenure analysis (⏱️ ELAPSED TIME - duration of employment)
    if tenure_col:
        is_valid, reason = SemanticValidator.is_valid_duration(df[tenure_col])
        
        if is_valid and pd.api.types.is_numeric_dtype(df[tenure_col]):
            valid_tenure = df[tenure_col].dropna()
            
            if not valid_tenure.empty:
                avg_tenure = valid_tenure.mean()
                median_tenure = valid_tenure.median()
                min_tenure = valid_tenure.min()
                max_tenure = valid_tenure.max()
                
                kpis.append(safe_kpi(
                    category="📅 Employee Tenure",
                    name="Avg Employee Tenure",
                    value=f"{avg_tenure:.1f} months",
                    formula="Mean(Tenure)",
                    source=f"`{tenure_col}`",
                    confidence=conf,
                    warnings="Low avg tenure - High turnover" if avg_tenure < 24 else warns
                ))
                
                kpis.append(safe_kpi(
                    category="📅 Employee Tenure",
                    name="Median Employee Tenure",
                    value=f"{median_tenure:.1f} months",
                    formula="Median(Tenure)",
                    source=f"`{tenure_col}`",
                    confidence=conf,
                    warnings=warns
                ))
                
                kpis.append(safe_kpi(
                    category="📅 Employee Tenure",
                    name="Min Tenure",
                    value=f"{min_tenure:.1f} months",
                    formula="Min(Tenure)",
                    source=f"`{tenure_col}`",
                    confidence=conf,
                    warnings=warns
                ))
                
                # Tenure distribution
                less_1yr = (valid_tenure < 12).sum()
                one_to_3yr = ((valid_tenure >= 12) & (valid_tenure < 36)).sum()
                over_3yr = (valid_tenure >= 36).sum()
                
                kpis.append(safe_kpi(
                    category="📅 Employee Tenure",
                    name="Employees < 1 Year",
                    value=f"{less_1yr:,} ({less_1yr/len(valid_tenure)*100:.1f}%)",
                    formula="Count(Tenure < 12 months)",
                    source=f"`{tenure_col}`",
                    confidence=conf,
                    warnings="High new hire ratio" if less_1yr/len(valid_tenure) > 0.3 else warns
                ))
                
                kpis.append(safe_kpi(
                    category="📅 Employee Tenure",
                    name="Employees 1-3 Years",
                    value=f"{one_to_3yr:,} ({one_to_3yr/len(valid_tenure)*100:.1f}%)",
                    formula="Count(Tenure 12-36 months)",
                    source=f"`{tenure_col}`",
                    confidence=conf,
                    warnings=warns
                ))
                
                kpis.append(safe_kpi(
                    category="📅 Employee Tenure",
                    name="Employees > 3 Years",
                    value=f"{over_3yr:,} ({over_3yr/len(valid_tenure)*100:.1f}%)",
                    formula="Count(Tenure >= 36 months)",
                    source=f"`{tenure_col}`",
                    confidence=conf,
                    warnings="Low long-term retention" if over_3yr/len(valid_tenure) < 0.3 else warns
                ))
        else:
            kpis.append(safe_kpi(
                category="📅 Employee Tenure",
                name="Tenure Metrics",
                value="EXCLUDED",
                formula="N/A",
                source=f"`{tenure_col}`",
                confidence="Low",
                warnings=f"Invalid duration: {reason}"
            ))
    
    # Exit type breakdown (OPERATIONAL only)
    if exit_type_col:
        exit_dist = df[exit_type_col].value_counts()
        
        if not exit_dist.empty:
            voluntary_mask = df[exit_type_col].astype(str).str.lower().isin(['voluntary', 'resignation', 'quit'])
            involuntary_mask = df[exit_type_col].astype(str).str.lower().isin(['involuntary', 'termination', 'layoff'])
            
            voluntary_count = voluntary_mask.sum()
            involuntary_count = involuntary_mask.sum()
            
            kpis.append(safe_kpi(
                category="👥 Workforce Stability",
                name="Voluntary Exits",
                value=f"{voluntary_count:,}",
                formula="Count(Exit Type = Voluntary)",
                source=f"`{exit_type_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="👥 Workforce Stability",
                name="Involuntary Exits",
                value=f"{involuntary_count:,}",
                formula="Count(Exit Type = Involuntary)",
                source=f"`{exit_type_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    return kpis
