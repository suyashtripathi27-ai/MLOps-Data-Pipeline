"""
Clinical trial enrollment, retention, dropout, and patient safety metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_clinical_metrics(df):
    """Calculates clinical trial and patient enrollment KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Enrollment is COUNT (number of patients), not time
    enrolled_col = first_column(df, ["enrolled_patients", "enrollment_count", "participant_count", "subjects"])
    dropout_col = first_column(df, ["dropouts", "dropout_count", "withdrawn", "screen_failures"])
    trial_col = first_column(df, ["trial_id", "study_id", "protocol_number"])
    # Trial duration is ELAPSED TIME (days/months in trial)
    duration_col = first_column(df, ["trial_duration_days", "duration_months", "study_length"])
    phase_col = first_column(df, ["phase", "trial_phase", "phase_type"])
    
    if not enrolled_col:
        return kpis
    
    # Enrollment is COUNT (patients), not duration
    if not pd.api.types.is_numeric_dtype(df[enrolled_col]):
        kpis.append(safe_kpi(
            category="🧪 Clinical Trials",
            name="Enrollment Metrics",
            value="EXCLUDED",
            formula="N/A",
            source=f"`{enrolled_col}`",
            confidence="Low",
            warnings="Enrollment column contains non-numeric data."
        ))
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [enrolled_col, dropout_col, trial_col, duration_col, phase_col] if col])
    
    # Total enrollment
    total_enrolled = df[enrolled_col].sum()
    avg_enrolled = df[enrolled_col].mean()
    
    kpis.append(safe_kpi(
        category="🧪 Clinical Trials",
        name="Total Enrolled Patients",
        value=f"{total_enrolled:,.0f}",
        formula="Sum(Enrolled Patients)",
        source=f"`{enrolled_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    kpis.append(safe_kpi(
        category="🧪 Clinical Trials",
        name="Avg Enrollment per Trial",
        value=f"{avg_enrolled:,.0f}",
        formula="Mean(Enrolled Patients)",
        source=f"`{enrolled_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Dropout analysis
    if dropout_col and pd.api.types.is_numeric_dtype(df[dropout_col]):
        total_dropouts = df[dropout_col].sum()
        dropout_rate = (total_dropouts / total_enrolled * 100) if total_enrolled > 0 else 0
        
        kpis.append(safe_kpi(
            category="🧪 Clinical Trials",
            name="Total Patient Dropouts",
            value=f"{total_dropouts:,.0f}",
            formula="Sum(Dropouts)",
            source=f"`{dropout_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="🧪 Clinical Trials",
            name="Clinical Dropout Rate",
            value=f"{dropout_rate:.2f}%",
            formula="(Total Dropouts / Total Enrolled) * 100",
            source=f"`{dropout_col}`, `{enrolled_col}`",
            confidence=conf,
            warnings="Critical retention risk (>15%)" if dropout_rate > 15 else "High dropout rate (>10%)" if dropout_rate > 10 else warns
        ))
    
    # Trial duration (⏱️ ELAPSED TIME - days/months in trial)
    if duration_col:
        is_valid, reason = SemanticValidator.is_valid_duration(df[duration_col])
        
        if is_valid and pd.api.types.is_numeric_dtype(df[duration_col]):
            valid_duration = df[duration_col].dropna()
            
            if not valid_duration.empty:
                avg_duration = valid_duration.mean()
                max_duration = valid_duration.max()
                
                kpis.append(safe_kpi(
                    category="📅 Trial Timeline",
                    name="Avg Trial Duration",
                    value=f"{avg_duration:.0f} days",
                    formula="Mean(Trial Duration)",
                    source=f"`{duration_col}`",
                    confidence=conf,
                    warnings="Long trial duration - Resource intensive" if avg_duration > 365 else warns
                ))
                
                kpis.append(safe_kpi(
                    category="📅 Trial Timeline",
                    name="Max Trial Duration",
                    value=f"{max_duration:.0f} days",
                    formula="Max(Trial Duration)",
                    source=f"`{duration_col}`",
                    confidence=conf,
                    warnings=warns
                ))
        else:
            kpis.append(safe_kpi(
                category="📅 Trial Timeline",
                name="Trial Duration Metrics",
                value="EXCLUDED",
                formula="N/A",
                source=f"`{duration_col}`",
                confidence="Low",
                warnings=f"Invalid duration: {reason}"
            ))
    
    # Trial phase breakdown
    if phase_col:
        phase_dist = df[phase_col].value_counts()
        
        if not phase_dist.empty:
            kpis.append(safe_kpi(
                category="🧪 Clinical Trials",
                name="Trial Distribution by Phase",
                value=f"Phases: {', '.join([f'{k}({v})' for k, v in phase_dist.head(3).items()])}",
                formula="Count(Distinct Phases)",
                source=f"`{phase_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    return kpis
