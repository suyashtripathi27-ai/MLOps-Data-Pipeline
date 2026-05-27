"""
Energy consumption, intensity, and efficiency metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

MANUFACTURING_CONFIG = {
    "missing_data_threshold": 6,
    "score_deduction_for_warning": 15,
    "low_confidence_threshold": 30,
}

def calc_energy_metrics(df, enable_debug=False):
    """
    Calculates energy consumption and intensity KPIs with optional execution tracing.
    
    Args:
        df: Input DataFrame
        enable_debug: If True, prints execution trace log for observability
    
    Returns:
        List of KPI dictionaries
    """
    engine = KPIEngine(df, industry_config=MANUFACTURING_CONFIG)
    if enable_debug:
        engine.enable_tracing()
    
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    energy_col, energy_series = engine.get_numeric(["energy_kwh", "power_consumption_kwh", "electricity_kwh"])
    intensity_col, intensity_series = engine.get_numeric(["energy_intensity", "kwh_per_unit"])
    gas_col, gas_series = engine.get_numeric(["gas_usage", "gas_consumption", "steam_usage"])
    
    # ==========================================
    # 1. ELECTRICITY USAGE
    # ==========================================
    if energy_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        energy_clean = energy_series.dropna()
        
        if len(energy_clean) > 0:
            total_energy = energy_clean.sum()
            avg_energy = energy_clean.mean()
            
            kpis.append(engine.build_kpi(
                category="🔌 Energy",
                name="Total Electricity Usage",
                value=f"{total_energy:,.1f} kWh",
                formula="Sum(Electricity)",
                source=f"`{energy_col}`"
            ))
            
            kpis.append(engine.build_kpi(
                category="🔌 Energy",
                name="Avg Electricity Usage",
                value=f"{avg_energy:,.1f} kWh",
                formula="Mean(Electricity)",
                source=f"`{energy_col}`"
            ))
        else:
            kpis.append(engine.log_missing("🔌 Energy", "Electricity", "All energy entries are missing/null."))
    else:
        kpis.append(engine.log_missing("🔌 Energy", "Electricity", "Missing numeric 'energy_kwh' column."))
    
    # ==========================================
    # 2. ENERGY INTENSITY
    # ==========================================
    if intensity_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        intensity_clean = intensity_series.dropna()
        
        if len(intensity_clean) > 0:
            avg_intensity = intensity_clean.mean()
            max_intensity = intensity_clean.max()
            
            kpis.append(engine.build_kpi(
                category="🔌 Energy",
                name="Avg Energy Intensity",
                value=f"{avg_intensity:,.2f} kWh/unit",
                formula="Mean(Energy Intensity)",
                source=f"`{intensity_col}`"
            ))
            
            kpis.append(engine.build_kpi(
                category="🔌 Energy",
                name="Max Energy Intensity",
                value=f"{max_intensity:,.2f} kWh/unit",
                formula="Max(Energy Intensity)",
                source=f"`{intensity_col}`"
            ))
        else:
            kpis.append(engine.log_missing("🔌 Energy", "Intensity", "All intensity entries are missing/null."))
    else:
        kpis.append(engine.log_missing("🔌 Energy", "Intensity", "Missing numeric 'energy_intensity' column."))
    
    # ==========================================
    # 3. GAS / THERMAL USAGE
    # ==========================================
    if gas_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        gas_clean = gas_series.dropna()
        
        if len(gas_clean) > 0:
            total_gas = gas_clean.sum()
            avg_gas = gas_clean.mean()
            
            kpis.append(engine.build_kpi(
                category="🔌 Energy",
                name="Total Gas / Thermal Usage",
                value=f"{total_gas:,.1f} units",
                formula="Sum(Gas Usage)",
                source=f"`{gas_col}`"
            ))
            
            kpis.append(engine.build_kpi(
                category="🔌 Energy",
                name="Avg Gas / Thermal Usage",
                value=f"{avg_gas:,.1f} units",
                formula="Mean(Gas Usage)",
                source=f"`{gas_col}`"
            ))
        else:
            kpis.append(engine.log_missing("🔌 Energy", "Gas Usage", "All gas entries are missing/null."))
    else:
        kpis.append(engine.log_missing("🔌 Energy", "Gas Usage", "Missing numeric 'gas_usage' column."))
    
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
