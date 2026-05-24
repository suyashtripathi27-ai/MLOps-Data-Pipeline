"""
Regulatory submissions, approvals, and market authorization metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_regulatory_metrics(df):
    """Calculates regulatory and approval KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Regulatory metrics are COUNT (submissions, approvals), not time
    submission_col = first_column(df, ["submission_id", "regulatory_submission", "dossier_id"])
    approval_col = first_column(df, ["approval_count", "approved_indications", "approved"])
    product_col = first_column(df, ["product_id", "drug_name", "product"])
    region_col = first_column(df, ["region", "regulatory_region", "market"])
    status_col = first_column(df, ["status", "submission_status", "approval_status"])
    
    if not submission_col and not approval_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [submission_col, approval_col, product_col, region_col, status_col] if col])
    
    # Total submissions
    if submission_col:
        total_submissions = df[submission_col].nunique()
        
        kpis.append(safe_kpi(
            category="📋 Regulatory",
            name="Total Regulatory Submissions",
            value=f"{total_submissions:,}",
            formula="Count(Distinct Submissions)",
            source=f"`{submission_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Approvals
    if approval_col and pd.api.types.is_numeric_dtype(df[approval_col]):
        total_approvals = df[approval_col].sum()
        
        kpis.append(safe_kpi(
            category="📋 Regulatory",
            name="Total Regulatory Approvals",
            value=f"{total_approvals:,}",
            formula="Sum(Approvals)",
            source=f"`{approval_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        # Approval rate
        if submission_col:
            total_submissions = df[submission_col].nunique()
            
            if total_submissions > 0:
                approval_rate = (total_approvals / total_submissions * 100)
                
                kpis.append(safe_kpi(
                    category="📋 Regulatory",
                    name="Submission Approval Rate",
                    value=f"{approval_rate:.2f}%",
                    formula="(Approvals / Submissions) * 100",
                    source=f"`{approval_col}`, `{submission_col}`",
                    confidence=conf,
                    warnings=warns
                ))
    
    # Status breakdown
    if status_col:
        status_lower = df[status_col].astype(str).str.lower()
        
        approved = status_lower.str.contains("approved|granted", na=False).sum()
        pending = status_lower.str.contains("pending|under review|submitted", na=False).sum()
        rejected = status_lower.str.contains("rejected|refused", na=False).sum()
        
        kpis.append(safe_kpi(
            category="📋 Regulatory",
            name="Approved Submissions",
            value=f"{approved:,}",
            formula="Count(Status = Approved)",
            source=f"`{status_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="📋 Regulatory",
            name="Pending Submissions",
            value=f"{pending:,}",
            formula="Count(Status = Pending)",
            source=f"`{status_col}`",
            confidence=conf,
            warnings="High pending submissions - Follow up" if pending > 5 else warns
        ))
        
        if rejected > 0:
            kpis.append(safe_kpi(
                category="📋 Regulatory",
                name="Rejected Submissions",
                value=f"{rejected:,}",
                formula="Count(Status = Rejected)",
                source=f"`{status_col}`",
                confidence=conf,
                warnings="⚠️ Review rejection reasons" if rejected > 0 else warns
            ))
    
    # Top product
    if product_col and approval_col and pd.api.types.is_numeric_dtype(df[approval_col]):
        product_approvals = df.groupby(product_col)[approval_col].sum().sort_values(ascending=False)
        
        if not product_approvals.empty:
            top_product = product_approvals.idxmax()
            top_approvals = product_approvals.max()
            
            kpis.append(safe_kpi(
                category="📋 Regulatory",
                name="Most Approved Product",
                value=f"{top_product} ({top_approvals:,} approvals)",
                formula="Product with max approvals",
                source=f"`{product_col}`, `{approval_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    return kpis
