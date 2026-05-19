from .customer_analysis import calc_customer_metrics
from .department_analysis import calc_department_metrics
from .inventory_analysis import calc_inventory_metrics
from .pricing_analysis import calc_pricing_metrics
from .promotion_analysis import calc_promotion_metrics
from .sales_analysis import calc_sales_metrics
from .seasonality_analysis import calc_seasonality_metrics
from .store_analysis import calc_store_metrics
from .workforce_analysis import calc_workforce_metrics


def generate_retail_kpis(df):
    """Consolidates all retail KPI generators into one list."""
    all_kpis = []
    all_kpis.extend(calc_sales_metrics(df))
    all_kpis.extend(calc_store_metrics(df))
    all_kpis.extend(calc_department_metrics(df))
    all_kpis.extend(calc_inventory_metrics(df))
    all_kpis.extend(calc_seasonality_metrics(df))
    all_kpis.extend(calc_pricing_metrics(df))
    all_kpis.extend(calc_customer_metrics(df))
    all_kpis.extend(calc_promotion_metrics(df))
    all_kpis.extend(calc_workforce_metrics(df))
    return all_kpis
