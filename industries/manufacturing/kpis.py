from .production_analysis import calc_production_metrics
from .quality_analysis import calc_quality_metrics
from .maintenance_analysis import calc_maintenance_metrics
from .supply_chain_analysis import calc_supply_chain_metrics


def generate_manufacturing_kpis(df):
    """Consolidates all manufacturing KPI generators into one list."""
    all_kpis = []
    all_kpis.extend(calc_production_metrics(df))
    all_kpis.extend(calc_quality_metrics(df))
    all_kpis.extend(calc_maintenance_metrics(df))
    all_kpis.extend(calc_supply_chain_metrics(df))
    return all_kpis
