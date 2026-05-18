import pandas as pd
import os
import zipfile
import io
from .relationship_detector import enrich_fact_table

def load_and_clean(file_path):
    """Loads files, handles massive database ZIPs, and enriches fact tables."""
    print(f"📥 Attempting to load: {file_path}")
    
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
        
    elif file_path.endswith('.zip'):
        print(f"📦 Inspecting ZIP archive for Star Schema...")
        with zipfile.ZipFile(file_path, 'r') as z:
            csv_files = [f for f in z.namelist() if f.endswith('.csv') and not f.startswith('__MACOSX')]
            
            if not csv_files:
                raise ValueError("No CSV files found in the ZIP archive.")
                
            if len(csv_files) == 1:
                target_file = csv_files[0]
                with z.open(target_file) as f:
                    df = pd.read_csv(f)
            else:
                print(f"⚠️ Multiple CSVs detected ({len(csv_files)}). Scanning for primary fact table...")
                core_keywords = ['trip', 'load', 'delivery', 'order', 'sales']
                target_file = None
                for f in csv_files:
                    if any(k in f.lower() for k in core_keywords):
                        target_file = f
                        break
                        
                if not target_file:
                    file_sizes = {f: z.getinfo(f).file_size for f in csv_files}
                    target_file = max(file_sizes, key=file_sizes.get)
                    
                print(f"🎯 Fact Table Selected: {target_file}")
                
                # 1. Load the Fact Table
                with z.open(target_file) as f:
                    fact_df = pd.read_csv(f)
                    
                # 2. Safely load Dimension Tables (Memory Guardrail: Skip if > 50MB)
                dim_dfs = {}
                for f_name in csv_files:
                    if f_name != target_file:
                        file_size_mb = z.getinfo(f_name).file_size / (1024 * 1024)
                        if file_size_mb < 50.0:
                            with z.open(f_name) as f:
                                # Store it in the dictionary using the filename without '.csv'
                                table_name = f_name.replace('.csv', '').split('/')[-1]
                                dim_dfs[table_name] = pd.read_csv(f)
                        else:
                            print(f"⏭️ Skipping `{f_name}` (Size: {file_size_mb:.1f}MB exceeds dimension limit)")
                            
                # 3. 🧠 THE MAGIC: Enrich the Fact Table
                df = enrich_fact_table(fact_df, dim_dfs)
                
    elif file_path.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(file_path)
    else:
        raise ValueError("❌ Unsupported file format.")
        
    df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
    print(f"🧹 Base load complete. Initial Shape: {df.shape}")
    return df

# ==========================================
# 2. UNIVERSAL DATA ENGINEERING
# ==========================================
def standardize_column_names(df):
    """Converts all columns to lowercase and replaces spaces with underscores."""
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    return df

def remove_duplicates(df):
    """Drops exact duplicate rows and returns the cleaned dataframe."""
    initial_shape = df.shape[0]
    df = df.drop_duplicates()
    final_shape = df.shape[0]
    if initial_shape != final_shape:
        print(f"🧹 Dropped {initial_shape - final_shape} duplicate rows.")
    return df

def fill_numeric_missing(df, strategy='median'):
    """Fills missing numeric values universally."""
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        if df[col].isnull().sum() > 0:
            if strategy == 'median':
                df[col] = df[col].fillna(df[col].median())
            elif strategy == 'mean':
                df[col] = df[col].fillna(df[col].mean())
    return df

def fix_datetime_columns(df):
    """Attempts to auto-detect and fix datetime columns."""
    for col in df.columns:
        if 'date' in col.lower() or 'time' in col.lower():
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass # If it fails, leave it as is
    return df

def apply_schema_aliases(df):
    """Maps known messy column names to our standard internal schema."""
    alias_dict = {
        "revenue": [
            "rev", "total_revenue", "income", "sales", "trip_revenue", 
            "freight_revenue", "billed_amount", "gross_revenue", "stat_value"
        ],
        "total_cost": [
            "cost", "total_expenses", "trip_cost", "overall_cost", 
            "freight_cost", "carrier_fee", "invoice_total"
        ],
        "detention_minutes": [
            "detention_time", "wait_time", "facility_delay", "dwell_time", 
            "delay_mins", "hold_time", "idle_time_hours", "detention_mins", "waiting_time"
        ],
        "actual_duration_hours": [
            "transit_days", "shipping_duration", "time_in_transit", 
            "lead_time", "actual_transit_time", "delivery_days"
        ],
        "temperature_celsius": ["temperature", "ambient_temp", "temp_c"],
        "asset_utilization_pct": ["asset_utilization", "utilization_rate", "capacity_used"],
        "delay_flag": ["logistics_delay", "delay_occurred", "is_delayed"
        ],
        "source_name": [
            "origin_warehouse", "facility_name", "origin_hub", "warehouse", 
            "pickup_location", "dispatch_location", "shipper_facility"
        ],
        "destination_name": [
            "destination", "delivery_location", "consignee_facility", 
            "drop_off", "final_destination", "receiving_hub"
        ],
        "actual_distance_miles": [
            "distance", "total_distance", "trip_miles", "route_distance", "miles_driven"
        ],
        "shipment_id": [
            "pro_number", "bol_number", "tracking_number", "load_id", 
            "order_id", "sid", "reference_number", "docket_number"
        ],
        "carrier_name": [
            "carrier", "scac", "transport_company", "logistics_provider", "trucking_company"
        ],
        "total_weight": [
            "weight_kg", "weight", "payload_weight", "cargo_weight", 
            "gross_weight", "net_mass", "weight_lbs"
        ]
    }
    
    for standard_name, messy_aliases in alias_dict.items():
        if standard_name not in df.columns:
            for alias in messy_aliases:
                if alias in df.columns:
                    df.rename(columns={alias: standard_name}, inplace=True)
                    print(f"🔄 Schema Mapper: Renamed `{alias}` to `{standard_name}`")
                    break
                    
    return df

def universal_clean(df):
    """The master function to run all universal cleaning steps."""
    print("⚙️ Running universal data engineering layers...")
    df = standardize_column_names(df)
    df = apply_schema_aliases(df)
    df = remove_duplicates(df)
    df = fill_numeric_missing(df)
    df = fix_datetime_columns(df)
    return df
