"""
Universal Categorical Analytics Module.
Detects status distributions, multi-entity concentration risks, and cross-tabulated performance variance across any industry dataset.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

def calc_universal_categorical_metrics(df: pd.DataFrame) -> list:
    """Calculates universal categorical KPIs (Status rates, Variance, Concentration)."""
    engine = KPIEngine(df)
    kpis = []
    
    if len(df) == 0: 
        return kpis

    # Fetch threshold from config if it exists, otherwise default to 40%
    concentration_threshold = getattr(engine, 'config', {}).get("concentration_threshold", 40.0)

    # Enterprise Lexicon Expansion
    negative_keywords = [
        'delay', 'delayed', 'lost', 'loss', 'failed', 'failure', 
        'rejected', 'rework', 'cancelled', 'cancel', 'breach', 
        'violation', 'deviation', 'defect', 'damaged', 'expired', 
        'attrition', 'terminated', 'overdue', 'default'
    ]

    # ---------------------------------------------------------
    # STATUS & FRICTION ANALYSIS
    # ---------------------------------------------------------
    status_col, status_series = engine.get_column(['status', 'state', 'condition', 'stage', 'outcome', 'claim_status', 'policy_status_ins', 'loan_status'])
    negative_counts = {}
    negative_rate = 0.0
    
    if status_col is not None:
        val_counts = status_series.value_counts(normalize=True) * 100
        
        for status_val, pct in val_counts.items():
            if any(word in str(status_val).lower() for word in negative_keywords):
                negative_counts[status_val] = pct
                
        negative_rate = sum(negative_counts.values())
        
        # Overall Friction Rate
        kpis.append(engine.build_kpi(
            category="📊 Categorical Distributions", 
            name="Workflow Friction Rate",
            value=f"{negative_rate:.1f}%", 
            formula="% of rows with negative status", 
            source=f"`{status_col}`",
            warnings="High friction rate detected" if negative_rate > 10 else "None"
        ))
        
        # Top Negative Status Isolation
        if negative_counts:
            top_neg_status = max(negative_counts, key=negative_counts.get)
            top_neg_pct = negative_counts[top_neg_status]
            kpis.append(engine.build_kpi(
                category="📊 Categorical Distributions", 
                name="Top Negative Status",
                value=f"{top_neg_status} ({top_neg_pct:.1f}%)", 
                formula="Max(Negative Statuses)", 
                source=f"`{status_col}`"
            ))

    # ---------------------------------------------------------
    # MULTI-ENTITY LOOPING & CONCENTRATION RISK
    # ---------------------------------------------------------
    entity_keywords = [
        'carrier', 'supplier', 'vendor', 'department', 'segment', 
        'region', 'warehouse', 'location', 'store_type', 'facility', 'policy_type'
    ]
    
    entity_cols = [col for col in df.columns if any(k in col.lower() for k in entity_keywords)]
    
    # Limit to top 3 entity columns to prevent LLM token overflow
    for entity_col in entity_cols[:3]:
        entity_series = df[entity_col]
        total_entities = entity_series.nunique()
        
        if total_entities == 0 or total_entities > 50:
            continue
            
        val_counts = entity_series.value_counts(normalize=True) * 100
        top_entity = val_counts.index[0]
        top_entity_pct = val_counts.iloc[0]
        
        is_risk = top_entity_pct > concentration_threshold
        
        kpis.append(engine.build_kpi(
            category=f"⚠️ Concentration Risk", 
            name=f"Top {entity_col.replace('_', ' ').title()} Dependency",
            value=f"{top_entity} ({top_entity_pct:.1f}%)", 
            formula=f"Max % share of {entity_col}", 
            source=f"`{entity_col}`",
            warnings=f"High dependency (> {concentration_threshold}%)" if is_risk else "None"
        ))
        
        # ---------------------------------------------------------
        # CROSS-TABULATED ENTITY PERFORMANCE VARIANCE
        # ---------------------------------------------------------
        if status_col is not None and negative_rate > 0:
            def calc_neg_pct(group):
                total = len(group)
                neg = sum(1 for val in group if any(w in str(val).lower() for w in negative_keywords))
                return (neg / total) * 100 if total > 0 else 0
                
            entity_risk_rates = df.groupby(entity_col)[status_col].apply(calc_neg_pct)
            
            if len(entity_risk_rates) > 1:
                worst_entity = entity_risk_rates.idxmax()
                worst_rate = entity_risk_rates.max()
                
                if worst_rate > 0:
                    kpis.append(engine.build_kpi(
                        category=f"⚠️ Risk Variance", 
                        name=f"Highest Failure Rate ({entity_col})",
                        value=f"{worst_entity} ({worst_rate:.1f}%)", 
                        formula=f"Max Negative Rate grouped by {entity_col}", 
                        source=f"`{entity_col}`, `{status_col}`",
                        warnings="Critical performance variance" if worst_rate > (negative_rate * 1.5) else "None"
                    ))

    return kpis
