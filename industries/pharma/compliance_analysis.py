"""
Regulatory compliance, audit findings, and GMP adherence metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

PHARMA_CONFIG = {
    "missing_data_threshold": 6,
    "score_deduction_for_warning": 15,
    "low_confidence_threshold": 30,
}

def calc_compliance_metrics(df, enable_debug=False):
    """
    Calculates regulatory compliance and GMP KPIs with optional execution tracing.
    
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
    
    # Compliance metrics are COUNT (number of findings/deviations), not time
    audit_col, audit_series = engine.get_column(["audit_id", "audit_number", "inspection_id"])
    finding_col, finding_series = engine.get_numeric(["finding_count", "findings", "audit_findings"])
    severity_col, severity_series = engine.get_column(["severity", "finding_severity", "classification"])
    status_col, status_series = engine.get_column(["status", "compliance_status", "remediation_status"])
    
    # ==========================================
    # 1. TOTAL AUDITS
    # ==========================================
    if audit_col is not None:
        total_audits = audit_series.nunique()
        
        kpis.append(engine.build_kpi(
            category="✅ Compliance",
            name="Total Audits/Inspections",
            value=f"{total_audits:,}",
            formula="Count(Distinct Audits)",
            source=f"`{audit_col}`"
        ))
    else:
        kpis.append(engine.log_missing("✅ Compliance", "Audits", "Missing 'audit_id' column."))
    
    # ==========================================
    # 2. TOTAL FINDINGS
    # ==========================================
    if finding_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        finding_clean = finding_series.dropna()
        
        if len(finding_clean) > 0:
            total_findings = finding_clean.sum()
            avg_findings = finding_clean.mean()
            
            warn_msg = "High finding volume - Review QMS (>20)" if total_findings > 20 else "None"
            kpis.append(engine.build_kpi(
                category="✅ Compliance",
                name="Total Audit Findings",
                value=f"{total_findings:,}",
                formula="Sum(Findings)",
                source=f"`{finding_col}`",
                warnings=warn_msg
            ))
            
            kpis.append(engine.build_kpi(
                category="✅ Compliance",
                name="Avg Findings per Audit",
                value=f"{avg_findings:.2f}",
                formula="Mean(Findings)",
                source=f"`{finding_col}`"
            ))
        else:
            kpis.append(engine.log_missing("✅ Compliance", "Findings", "All finding entries are missing/null."))
    else:
        kpis.append(engine.log_missing("✅ Compliance", "Findings", "Missing numeric 'finding_count' column."))
    
    # ==========================================
    # 3. SEVERITY BREAKDOWN
    # ==========================================
    if severity_col is not None:
        # FIX: Drop NaN BEFORE converting to string
        severity_clean = severity_series.dropna().astype(str).str.lower()
        
        # FIX: Use cleaned series length for accurate counts
        total_severity = len(severity_clean)
        
        if total_severity > 0:
            critical = severity_clean.str.contains("critical|warning letter", na=False).sum()
            major = severity_clean.str.contains("major|significant", na=False).sum()
            minor = severity_clean.str.contains("minor|observation", na=False).sum()
            
            warn_msg = "⚠️ CRITICAL: Immediate action required" if critical > 0 else "None"
            kpis.append(engine.build_kpi(
                category="✅ Compliance",
                name="Critical Findings",
                value=f"{critical:,}",
                formula="Count(Severity = Critical)",
                source=f"`{severity_col}`",
                warnings=warn_msg
            ))
            
            if critical == 0:
                warn_msg = "Review and close findings" if major > 5 else "None"
                kpis.append(engine.build_kpi(
                    category="✅ Compliance",
                    name="Major Findings",
                    value=f"{major:,}",
                    formula="Count(Severity = Major)",
                    source=f"`{severity_col}`",
                    warnings=warn_msg
                ))
        else:
            kpis.append(engine.log_missing("✅ Compliance", "Severity", "All severity entries are missing/null."))
    else:
        kpis.append(engine.log_missing("✅ Compliance", "Severity", "Missing 'severity' column."))
    
    # ==========================================
    # 4. REMEDIATION STATUS
    # ==========================================
    if status_col is not None:
        # FIX: Drop NaN BEFORE converting to string
        status_clean = status_series.dropna().astype(str).str.lower()
        
        # FIX: Use cleaned series length for accurate counts
        total_status = len(status_clean)
        
        if total_status > 0:
            closed = status_clean.str.contains("closed|resolved|complete", na=False).sum()
            open_findings = status_clean.str.contains("open|pending|in-progress", na=False).sum()
            
            if total_status > 0:
                closure_rate = (closed / total_status * 100)
                
                warn_msg = "Slow remediation progress (<50%)" if closure_rate < 50 else "None"
                kpis.append(engine.build_kpi(
                    category="✅ Compliance",
                    name="Finding Closure Rate",
                    value=f"{closure_rate:.2f}%",
                    formula="(Closed / Total Valid) * 100",
                    source=f"`{status_col}`",
                    warnings=warn_msg
                ))
                
                warn_msg = "High number of pending remediations (>10)" if open_findings > 10 else "None"
                kpis.append(engine.build_kpi(
                    category="✅ Compliance",
                    name="Open Findings",
                    value=f"{open_findings:,}",
                    formula="Count(Status = Open)",
                    source=f"`{status_col}`",
                    warnings=warn_msg
                ))
        else:
            kpis.append(engine.log_missing("✅ Compliance", "Status", "All status entries are missing/null."))
    else:
        kpis.append(engine.log_missing("✅ Compliance", "Status", "Missing 'status' column."))
    
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
