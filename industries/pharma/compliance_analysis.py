"""
Regulatory compliance, audit findings, and GMP adherence metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_compliance_metrics(df):
    """Calculates regulatory compliance and GMP KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Compliance metrics are COUNT (number of findings/deviations), not time
    audit_col = first_column(df, ["audit_id", "audit_number", "inspection_id"])
    finding_col = first_column(df, ["finding_count", "findings", "audit_findings"])
    severity_col = first_column(df, ["severity", "finding_severity", "classification"])
    status_col = first_column(df, ["status", "compliance_status", "remediation_status"])
    
    if not finding_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [audit_col, finding_col, severity_col, status_col] if col])
    
    # Total audits
    if audit_col:
        total_audits = df[audit_col].nunique()
        
        kpis.append(safe_kpi(
            category="✅ Compliance",
            name="Total Audits/Inspections",
            value=f"{total_audits:,}",
            formula="Count(Distinct Audits)",
            source=f"`{audit_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Total findings
    if finding_col and pd.api.types.is_numeric_dtype(df[finding_col]):
        total_findings = df[finding_col].sum()
        avg_findings = df[finding_col].mean()
        
        kpis.append(safe_kpi(
            category="✅ Compliance",
            name="Total Audit Findings",
            value=f"{total_findings:,}",
            formula="Sum(Findings)",
            source=f"`{finding_col}`",
            confidence=conf,
            warnings="High finding volume - Review QMS" if total_findings > 20 else warns
        ))
        
        kpis.append(safe_kpi(
            category="✅ Compliance",
            name="Avg Findings per Audit",
            value=f"{avg_findings:.2f}",
            formula="Mean(Findings)",
            source=f"`{finding_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Severity breakdown
    if severity_col:
        severity_lower = df[severity_col].astype(str).str.lower()
        
        critical = severity_lower.str.contains("critical|warning letter", na=False).sum()
        major = severity_lower.str.contains("major|significant", na=False).sum()
        minor = severity_lower.str.contains("minor|observation", na=False).sum()
        
        kpis.append(safe_kpi(
            category="✅ Compliance",
            name="Critical Findings",
            value=f"{critical:,}",
            formula="Count(Severity = Critical)",
            source=f"`{severity_col}`",
            confidence=conf,
            warnings="⚠️ CRITICAL: Immediate action required" if critical > 0 else warns
        ))
        
        if critical == 0:
            kpis.append(safe_kpi(
                category="✅ Compliance",
                name="Major Findings",
                value=f"{major:,}",
                formula="Count(Severity = Major)",
                source=f"`{severity_col}`",
                confidence=conf,
                warnings="Review and close findings" if major > 5 else warns
            ))
    
    # Remediation status
    if status_col:
        status_lower = df[status_col].astype(str).str.lower()
        
        closed = status_lower.str.contains("closed|resolved|complete", na=False).sum()
        open_findings = status_lower.str.contains("open|pending|in-progress", na=False).sum()
        
        total_status = closed + open_findings
        
        if total_status > 0:
            closure_rate = (closed / total_status * 100)
            
            kpis.append(safe_kpi(
                category="✅ Compliance",
                name="Finding Closure Rate",
                value=f"{closure_rate:.2f}%",
                formula="(Closed / Total) * 100",
                source=f"`{status_col}`",
                confidence=conf,
                warnings="Slow remediation progress" if closure_rate < 50 else warns
            ))
            
            kpis.append(safe_kpi(
                category="✅ Compliance",
                name="Open Findings",
                value=f"{open_findings:,}",
                formula="Count(Status = Open)",
                source=f"`{status_col}`",
                confidence=conf,
                warnings="High number of pending remediations" if open_findings > 10 else warns
            ))
    
    return kpis
