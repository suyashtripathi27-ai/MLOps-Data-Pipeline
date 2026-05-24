"""
Pharmacovigilance, adverse events, and safety signal detection metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_adverse_events_metrics(df):
    """Calculates adverse event and safety KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Adverse events are COUNT (number of events), not time
    sae_col = first_column(df, ["sae_count", "serious_adverse_events", "serious_events", "sar_count"])
    ae_col = first_column(df, ["adverse_event_count", "ae_count", "total_ae"])
    severity_col = first_column(df, ["severity", "event_severity", "grade"])
    patient_col = first_column(df, ["patient_id", "subject_id", "participant_id"])
    
    if not sae_col and not ae_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [sae_col, ae_col, severity_col, patient_col] if col])
    
    # Serious Adverse Events (SAE)
    if sae_col and pd.api.types.is_numeric_dtype(df[sae_col]):
        total_sae = df[sae_col].sum()
        avg_sae = df[sae_col].mean()
        
        kpis.append(safe_kpi(
            category="⚠️ Pharmacovigilance",
            name="Total Serious Adverse Events (SAE)",
            value=f"{total_sae:,.0f}",
            formula="Sum(SAE Count)",
            source=f"`{sae_col}`",
            confidence=conf,
            warnings="High SAE volume - Signal investigation required" if total_sae > 50 else warns
        ))
        
        kpis.append(safe_kpi(
            category="⚠️ Pharmacovigilance",
            name="Avg SAE per Trial/Record",
            value=f"{avg_sae:.2f}",
            formula="Mean(SAE Count)",
            source=f"`{sae_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Total Adverse Events
    if ae_col and pd.api.types.is_numeric_dtype(df[ae_col]):
        total_ae = df[ae_col].sum()
        
        kpis.append(safe_kpi(
            category="⚠️ Pharmacovigilance",
            name="Total Adverse Events (AE)",
            value=f"{total_ae:,.0f}",
            formula="Sum(AE Count)",
            source=f"`{ae_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        # SAE/AE ratio
        if sae_col and pd.api.types.is_numeric_dtype(df[sae_col]):
            total_sae = df[sae_col].sum()
            sae_ratio = (total_sae / total_ae * 100) if total_ae > 0 else 0
            
            kpis.append(safe_kpi(
                category="⚠️ Pharmacovigilance",
                name="SAE as % of Total AE",
                value=f"{sae_ratio:.2f}%",
                formula="(Total SAE / Total AE) * 100",
                source=f"`{sae_col}`, `{ae_col}`",
                confidence=conf,
                warnings="High severity rate - Safety concern" if sae_ratio > 20 else warns
            ))
    
    # Severity analysis
    if severity_col:
        severity_lower = df[severity_col].astype(str).str.lower()
        
        severe_count = severity_lower.str.contains("severe|grade 3|grade 4|life-threatening", na=False).sum()
        moderate_count = severity_lower.str.contains("moderate|grade 2", na=False).sum()
        mild_count = severity_lower.str.contains("mild|grade 1|minimal", na=False).sum()
        
        total_events = severe_count + moderate_count + mild_count
        
        kpis.append(safe_kpi(
            category="⚠️ Pharmacovigilance",
            name="Severe Events (Grade 3/4)",
            value=f"{severe_count:,}",
            formula="Count(Severity IN (Severe, Grade 3/4))",
            source=f"`{severity_col}`",
            confidence=conf,
            warnings="Critical: Grade 3/4 events present" if severe_count > 0 else warns
        ))
        
        if total_events > 0:
            severe_pct = (severe_count / total_events * 100)
            
            kpis.append(safe_kpi(
                category="⚠️ Pharmacovigilance",
                name="Severe Event Percentage",
                value=f"{severe_pct:.2f}%",
                formula="(Severe / Total) * 100",
                source=f"`{severity_col}`",
                confidence=conf,
                warnings="Elevated severity signal" if severe_pct > 10 else warns
            ))
    
    # Affected patients
    if patient_col:
        affected_patients = df[patient_col].nunique()
        
        kpis.append(safe_kpi(
            category="⚠️ Pharmacovigilance",
            name="Patients with AE",
            value=f"{affected_patients:,}",
            formula="Count(Distinct Patients with Events)",
            source=f"`{patient_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    return kpis
