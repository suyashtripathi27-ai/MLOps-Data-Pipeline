"""
Pharmacovigilance, adverse events, and safety signal detection metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

PHARMA_CONFIG = {
    "missing_data_threshold": 6,
    "score_deduction_for_warning": 15,
    "low_confidence_threshold": 30,
}

def calc_adverse_events_metrics(df, enable_debug=False):
    """
    Calculates adverse event and safety KPIs with optional execution tracing.
    
    Args:
        df: Input DataFrame
        enable_debug: If True, prints execution trace log for observability
    
    Returns:
        List of KPI dictionaries
    """
    engine = KPIEngine(df, industry_config=PHARMA_CONFIG)
    if enable_debug:
        engine.enable_tracing()
    
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Adverse events are COUNT (number of events), not time
    sae_col, sae_series = engine.get_numeric(["sae_count", "serious_adverse_events", "serious_events", "sar_count"])
    ae_col, ae_series = engine.get_numeric(["adverse_event_count", "ae_count", "total_ae"])
    severity_col, severity_series = engine.get_column(["severity", "event_severity", "grade"])
    patient_col, patient_series = engine.get_column(["patient_id", "subject_id", "participant_id"])
    
    # ==========================================
    # 1. SERIOUS ADVERSE EVENTS (SAE)
    # ==========================================
    if sae_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        sae_clean = sae_series.dropna()
        
        if len(sae_clean) > 0:
            total_sae = sae_clean.sum()
            avg_sae = sae_clean.mean()
            
            warn_msg = "High SAE volume - Signal investigation required (>50)" if total_sae > 50 else "None"
            kpis.append(engine.build_kpi(
                category="⚠️ Pharmacovigilance",
                name="Total Serious Adverse Events (SAE)",
                value=f"{total_sae:,.0f}",
                formula="Sum(SAE Count)",
                source=f"`{sae_col}`",
                warnings=warn_msg
            ))
            
            kpis.append(engine.build_kpi(
                category="⚠️ Pharmacovigilance",
                name="Avg SAE per Trial/Record",
                value=f"{avg_sae:.2f}",
                formula="Mean(SAE Count)",
                source=f"`{sae_col}`"
            ))
        else:
            kpis.append(engine.log_missing("⚠️ Pharmacovigilance", "SAE", "All SAE entries are missing/null."))
    else:
        kpis.append(engine.log_missing("⚠️ Pharmacovigilance", "SAE", "Missing numeric 'sae_count' column."))
    
    # ==========================================
    # 2. TOTAL ADVERSE EVENTS
    # ==========================================
    if ae_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        ae_clean = ae_series.dropna()
        
        if len(ae_clean) > 0:
            total_ae = ae_clean.sum()
            
            kpis.append(engine.build_kpi(
                category="⚠️ Pharmacovigilance",
                name="Total Adverse Events (AE)",
                value=f"{total_ae:,.0f}",
                formula="Sum(AE Count)",
                source=f"`{ae_col}`"
            ))
            
            # ==========================================
            # 3. SAE/AE RATIO
            # ==========================================
            if sae_col is not None:
                # FIX: Drop NaN values BEFORE calculating
                sae_ae_clean = pd.concat([sae_series, ae_series], axis=1).dropna()
                
                if len(sae_ae_clean) > 0:
                    total_sae = sae_ae_clean[sae_col].sum()
                    total_ae = sae_ae_clean[ae_col].sum()
                    
                    if total_ae > 0:
                        sae_ratio = (total_sae / total_ae * 100)
                        
                        warn_msg = "High severity rate - Safety concern (>20%)" if sae_ratio > 20 else "None"
                        kpis.append(engine.build_kpi(
                            category="⚠️ Pharmacovigilance",
                            name="SAE as % of Total AE",
                            value=f"{sae_ratio:.2f}%",
                            formula="(Total SAE / Total AE) * 100",
                            source=f"`{sae_col}`, `{ae_col}`",
                            warnings=warn_msg
                        ))
                else:
                    kpis.append(engine.log_missing("⚠️ Pharmacovigilance", "SAE/AE Ratio", "Missing valid SAE/AE data."))
            else:
                kpis.append(engine.log_missing("⚠️ Pharmacovigilance", "SAE/AE Ratio", "Missing 'sae_count' column."))
        else:
            kpis.append(engine.log_missing("⚠️ Pharmacovigilance", "AE", "All AE entries are missing/null."))
    else:
        kpis.append(engine.log_missing("⚠️ Pharmacovigilance", "AE", "Missing numeric 'adverse_event_count' column."))
    
    # ==========================================
    # 4. SEVERITY ANALYSIS
    # ==========================================
    if severity_col is not None:
        # FIX: Drop NaN BEFORE converting to string
        severity_clean = severity_series.dropna().astype(str).str.lower()
        
        # FIX: Use cleaned series length for accurate counts
        total_severity = len(severity_clean)
        
        if total_severity > 0:
            severe_count = severity_clean.str.contains("severe|grade 3|grade 4|life-threatening", na=False).sum()
            moderate_count = severity_clean.str.contains("moderate|grade 2", na=False).sum()
            mild_count = severity_clean.str.contains("mild|grade 1|minimal", na=False).sum()
            
            kpis.append(engine.build_kpi(
                category="⚠️ Pharmacovigilance",
                name="Severe Events (Grade 3/4)",
                value=f"{severe_count:,}",
                formula="Count(Severity IN (Severe, Grade 3/4))",
                source=f"`{severity_col}`",
                warnings="Critical: Grade 3/4 events present" if severe_count > 0 else "None"
            ))
            
            if total_severity > 0:
                severe_pct = (severe_count / total_severity * 100)
                
                warn_msg = "Elevated severity signal (>10%)" if severe_pct > 10 else "None"
                kpis.append(engine.build_kpi(
                    category="⚠️ Pharmacovigilance",
                    name="Severe Event Percentage",
                    value=f"{severe_pct:.2f}%",
                    formula="(Severe / Total Valid) * 100",
                    source=f"`{severity_col}`",
                    warnings=warn_msg
                ))
        else:
            kpis.append(engine.log_missing("⚠️ Pharmacovigilance", "Severity", "All severity entries are missing/null."))
    else:
        kpis.append(engine.log_missing("⚠️ Pharmacovigilance", "Severity", "Missing 'severity' column."))
    
    # ==========================================
    # 5. AFFECTED PATIENTS
    # ==========================================
    if patient_col is not None:
        affected_patients = patient_series.nunique()
        
        kpis.append(engine.build_kpi(
            category="⚠️ Pharmacovigilance",
            name="Patients with AE",
            value=f"{affected_patients:,}",
            formula="Count(Distinct Patients with Events)",
            source=f"`{patient_col}`"
        ))
    else:
        kpis.append(engine.log_missing("⚠️ Pharmacovigilance", "Affected Patients", "Missing 'patient_id' column."))
    
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
