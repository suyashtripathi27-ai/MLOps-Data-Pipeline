import pandas as pd
from utils.validator import SemanticValidator

def calc_inventory_metrics(df):
    """Calculates stockouts and inventory health with strict gatekeeping."""
    kpis = []
    
    if 'inventory_level' in df.columns:
        # 🛡️ GATEKEEPER: Ensure inventory counts aren't massively negative/corrupted
        is_valid, reason = SemanticValidator.is_valid_duration(df['inventory_level'])
        
        if is_valid:
            valid_inv = df['inventory_level'].dropna()
            if not valid_inv.empty:
                avg_inv = valid_inv.mean()
                # A stockout is when inventory drops to 0 or below
                stockout_rate = (valid_inv <= 0).sum() / len(valid_inv) * 100
                
                kpis.append({
                    "category": "📦 Inventory Health", "name": "Average Stock Level",
                    "value": f"{avg_inv:,.0f} units",
                    "source": "`inventory_level`"
                })
                kpis.append({
                    "category": "📦 Inventory Health", "name": "Stockout Rate",
                    "value": f"{stockout_rate:.1f}%",
                    "source": "`inventory_level`"
                })
        else:
            kpis.append({
                "category": "📦 Inventory Health", "name": "Inventory Metrics",
                "value": "EXCLUDED",
                "source": f"Data rejected: {reason}"
            })

    return kpis
