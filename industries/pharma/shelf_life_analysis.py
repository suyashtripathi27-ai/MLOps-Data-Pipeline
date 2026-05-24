"""
Product shelf life, expiration risk, and stability metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_shelf_life_metrics(df):
    """Calculates shelf life and expiration risk KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Shelf life is ELAPSED TIME (days/months product is valid)
    shelf_life_col = first_column(df, ["shelf_life_days", "shelf_life_months", "stability_duration", "expiry_period"])
    expiry_col = first_column(df, ["expiry_date", "exp_date", "expiration_date"])
    batch_col = first_column(df, ["batch_id", "lot_number", "batch_number"])
    product_col = first_column(df, ["product_id", "drug_name", "formulation"])
    
    if not shelf_life_col and not expiry_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [shelf_life_col, expiry_col, batch_col, product_col] if col])
    
    # Shelf life (⏱️ ELAPSED TIME - validate as duration)
    if shelf_life_col:
        is_valid, reason = SemanticValidator.is_valid_duration(df[shelf_life_col])
        
        if is_valid and pd.api.types.is_numeric_dtype(df[shelf_life_col]):
            valid_shelf = df[shelf_life_col].dropna()
            
            if not valid_shelf.empty:
                avg_shelf_life = valid_shelf.mean()
                min_shelf_life = valid_shelf.min()
                max_shelf_life = valid_shelf.max()
                
                kpis.append(safe_kpi(
                    category="📦 Shelf Life",
                    name="Avg Product Shelf Life",
                    value=f"{avg_shelf_life:.0f} days",
                    formula="Mean(Shelf Life)",
                    source=f"`{shelf_life_col}`",
                    confidence=conf,
                    warnings=warns
                ))
                
                kpis.append(safe_kpi(
                    category="📦 Shelf Life",
                    name="Min Shelf Life",
                    value=f"{min_shelf_life:.0f} days",
                    formula="Min(Shelf Life)",
                    source=f"`{shelf_life_col}`",
                    confidence=conf,
                    warnings="Short shelf life - Market advantage risk" if min_shelf_life < 365 else warns
                ))
                
                kpis.append(safe_kpi(
                    category="📦 Shelf Life",
                    name="Max Shelf Life",
                    value=f"{max_shelf_life:.0f} days",
                    formula="Max(Shelf Life)",
                    source=f"`{shelf_life_col}`",
                    confidence=conf,
                    warnings=warns
                ))
        else:
            kpis.append(safe_kpi(
                category="📦 Shelf Life",
                name="Shelf Life Metrics",
                value="EXCLUDED",
                formula="N/A",
                source=f"`{shelf_life_col}`",
                confidence="Low",
                warnings=f"Invalid duration: {reason}"
            ))
    
    # Expiration analysis
    if expiry_col:
        expiry_dt = pd.to_datetime(df[expiry_col], errors="coerce")
        dt_valid, reason = SemanticValidator.is_valid_datetime(expiry_dt.dropna())
        
        if dt_valid:
            today = pd.Timestamp.now()
            
            # Near-expiry (< 90 days)
            ninety_days_ahead = today + pd.Timedelta(days=90)
            near_expiry = ((expiry_dt <= ninety_days_ahead) & (expiry_dt >= today)).sum()
            
            # Expired
            expired = (expiry_dt < today).sum()
            
            # Future (valid)
            future_valid = (expiry_dt >= ninety_days_ahead).sum()
            
            total_valid = near_expiry + expired + future_valid
            
            kpis.append(safe_kpi(
                category="📦 Shelf Life",
                name="Near-Expiry Batches (<90 Days)",
                value=f"{near_expiry:,} batches",
                formula="Count(Expiry - Today < 90 Days)",
                source=f"`{expiry_col}`",
                confidence=conf,
                warnings="High expiry risk - Expedite distribution" if near_expiry > 10 else warns
            ))
            
            kpis.append(safe_kpi(
                category="📦 Shelf Life",
                name="Expired Batches",
                value=f"{expired:,} batches",
                formula="Count(Expiry < Today)",
                source=f"`{expiry_col}`",
                confidence=conf,
                warnings="⚠️ CRITICAL: Remove expired batches immediately" if expired > 0 else warns
            ))
            
            if total_valid > 0:
                near_expiry_pct = (near_expiry / total_valid * 100)
                expired_pct = (expired / total_valid * 100)
                
                kpis.append(safe_kpi(
                    category="📦 Shelf Life",
                    name="Expiration Risk %",
                    value=f"{near_expiry_pct + expired_pct:.2f}%",
                    formula="(Near-Expiry + Expired) / Total * 100",
                    source=f"`{expiry_col}`",
                    confidence=conf,
                    warnings="High expiration risk inventory" if (near_expiry_pct + expired_pct) > 20 else warns
                ))
        else:
            kpis.append(safe_kpi(
                category="📦 Shelf Life",
                name="Expiration Metrics",
                value="EXCLUDED",
                formula="N/A",
                source=f"`{expiry_col}`",
                confidence="Low",
                warnings=f"Invalid date: {reason}"
            ))
    
    return kpis
