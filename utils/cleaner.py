import pandas as pd
import os
import zipfile
import io
import difflib
import re
from .relationship_detector import enrich_fact_table

def load_and_clean(file_path):
    """Loads files, handles massive database ZIPs, and enriches fact tables."""
    print(f"📥 Attempting to load: {file_path}")
    
    if file_path.endswith('.csv'):
        # FIXED: Removed the stray z.open line that was accidentally placed here
        df = pd.read_csv(file_path, sep=None, engine='python', encoding='utf-8-sig')
        
    elif file_path.endswith('.zip'):
        print(f"📦 Inspecting ZIP archive for Star Schema...")
        with zipfile.ZipFile(file_path, 'r') as z:
            csv_files = [f for f in z.namelist() if f.endswith('.csv') and not f.startswith('__MACOSX')]
            if not csv_files: raise ValueError("No CSV files found in ZIP.")
            
            if len(csv_files) == 1:
                target_file = csv_files[0]
                # FIXED: Added the sniffer here
                with z.open(target_file) as f: df = pd.read_csv(f, sep=None, engine='python', encoding='utf-8-sig')
            else:
                core_keywords = ['trip', 'load', 'delivery', 'order', 'sales']
                target_file = next((f for f in csv_files if any(k in f.lower() for k in core_keywords)), None)
                if not target_file:
                    file_sizes = {f: z.getinfo(f).file_size for f in csv_files}
                    target_file = max(file_sizes, key=file_sizes.get)
                
                with z.open(target_file) as f: 
                    fact_df = pd.read_csv(f, sep=None, engine='python', encoding='utf-8-sig')
                
                dim_dfs = {}
                for f_name in csv_files:
                    if f_name != target_file and (z.getinfo(f_name).file_size / (1024 * 1024)) < 50.0:
                        with z.open(f_name) as f:
                            # FIXED: Added the sniffer here as well
                            dim_dfs[f_name.replace('.csv', '').split('/')[-1]] = pd.read_csv(f, sep=None, engine='python', encoding='utf-8-sig')
                            
                df = enrich_fact_table(fact_df, dim_dfs)
                
    elif file_path.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(file_path)
    else:
        raise ValueError("❌ Unsupported file format.")
        
    df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
    print(f"🧹 Base load complete. Initial Shape: {df.shape}")
    return df
# ==========================================
# 🧠 THE EVIDENCE-BASED SEMANTIC ENGINE
# ==========================================
UNIVERSAL_SCHEMA = {
    "revenue": ["rev", "totalrevenue", "income", "sales", "triprevenue", "freightrevenue", "billedamount", "grossrevenue", "statvalue", "amt", "amount"],
    "total_cost": ["cost", "totalexpenses", "tripcost", "overallcost", "freightcost", "carrierfee", "invoicetotal"],
    "detention_minutes": ["detentiontime", "waittime", "facilitydelay", "dwelltime", "delaymins", "holdtime", "idletimehours", "detentionmins", "waitingtime"],
    "actual_duration_hours": ["transitdays", "shippingduration", "timeintransit", "leadtime", "actualtransittime", "deliverydays", "triptm"],
    "temperature_celsius": ["temperature", "ambienttemp", "tempc"],
    "asset_utilization_pct": ["assetutilization", "utilizationrate", "capacityused"],
    "delay_flag": ["logisticsdelay", "delayoccurred", "isdelayed"],
    "source_name": ["originwarehouse", "facilityname", "originhub", "warehouse", "pickuplocation", "dispatchlocation", "shipperfacility", "srcwh"],
    "destination_name": ["destination", "deliverylocation", "consigneefacility", "dropoff", "finaldestination", "receivinghub", "destctr"],
    "actual_distance_miles": ["distance", "totaldistance", "tripmiles", "routedistance", "milesdriven"],
    "shipment_id": ["pronumber", "bolnumber", "trackingnumber", "loadid", "orderid", "sid", "referencenumber", "docketnumber"],
    "carrier_name": ["carrier", "scac", "transportcompany", "logisticsprovider", "truckingcompany"],
    "total_weight": ["weightkg", "weight", "payloadweight", "cargoweight", "grossweight", "netmass", "weightlbs"],
    "account_id": ["account_number", "acct_id", "acct_num", "account id", "Account No"],
    "transaction_date": ["date", "posting_date", "txn_date", "transaction date"],
    "amount": ["transaction_amount", "txn_amt", "value", "withdrawal", "deposit_amount"],
    "balance": ["account_balance", "ending_balance", "available_balance", "ledger_balance"],
    "customer_id": ["customer_code", "cust_id", "client_id"],
    "loan_status": ["status", "payment_status", "loan_state"],
    "outstanding_balance": ["loan_balance", "remaining_balance", "principal_remaining"],
    "fees_charged": ["fee_amount", "charges", "fee", "service_charge"],
    "aml_flag": ["aml_alert", "suspicious_flag", "fraud_flag", "is_suspicious"],
    "batch_id": ["batch_no", "lot_number", "lot_id", "production_batch"],
    "product_name": ["drug_name", "medication", "compound", "asset"],
    "therapeutic_area": ["category", "drug_class", "indication", "disease_area"],
    "manufacturing_date": ["mfg_date", "production_date", "date_of_manufacture"],
    "expiry_date": ["exp_date", "expiration", "valid_until", "use_by"],
    "quantity_produced": ["yield", "batch_size", "units_manufactured"],
    "quality_pass_rate": ["purity_score", "qa_rate", "yield_percent", "qc_score"],
    "regulatory_status": ["status", "fda_status", "approval_status", "qa_status"],
    "kyc_status": ["kyc_verified", "verification_status", "is_verified"],
    "enrolled": ["participants", "enrollment_count", "subjects"],
    "dropouts": ["dropout_count", "withdrawn", "lost_to_followup"],
    "sae_count": ["serious_adverse_events", "adverse_events", "ae_count"],
    "batch_yield": ["yield_percentage", "production_yield", "yield_rate"],
    "oos_rate": ["out_of_spec_rate", "deviations", "oos_count"],
    "rft_rate": ["right_first_time", "first_pass_yield", "rft"],
    "capa_count": ["corrective_actions", "preventive_actions", "capas"],
    "cold_chain_breaches": ["temp_excursions", "cold_chain_events", "temperature_breach"],
    "submission_date": ["nda_submission", "filing_date"],
    "approval_date": ["fda_approval", "ema_approval"],
    "complaints": ["complaint_count", "adverse_reports", "customer_complaints"],
    "forecast_demand": ["predicted_demand", "demand_forecast", "projected_sales"],
    "actual_demand": ["quantity_sold", "actual_sales"],
    "profit": ["netprofit", "netincome", "earnings", "netearnings", "profitamount"],
    "expense": ["expenses", "opex", "operatingexpense", "operating_expense", "operatingexpenses"],
    "assets": ["totalassets", "assettotal", "asset_value", "assetvalue"],
    "equity": ["shareholders_equity", "shareholderequity", "owner_equity", "ownersequity"],
    "current_assets": ["currentassets", "currassets", "currentasset", "currentassetstotal"],
    "current_liabilities": ["currentliabilities", "currliabilities", "currentliab", "currentliabs"],
    "cash": ["cashbalance", "cashamount", "cashonhand"],
    "inventory": ["stock_value", "stock", "inventory_value"],
    "operating_cashflow": ["cashfromoperations", "opcf", "operatingcf"],
    "investing_cashflow": ["cashfrominvesting", "invcf", "investingcf"],
    "financing_cashflow": ["cashfromfinancing", "fincf", "financingcf"],
    "investment_value": ["portfolio_value", "market_value", "investmentamount"],
    "return": ["roi", "pct_return", "investment_return"],
    "default_flag": ["defaulted", "is_default", "loan_default"],
    "machine_id": ["equipment_id", "asset_id", "work_center", "machine_name"],
    "production_line": ["line_id", "assembly_line", "workcell", "line_number"],
    "operator_id": ["worker_id", "employee_id", "technician", "operator"],
    "shift": ["shift_id", "working_shift", "shift_name"],
    "production_volume": ["actual_output", "units_produced", "good_units", "qty_produced", "total_yield"],
    "target_volume": ["planned_production", "target_output", "expected_units", "target_qty"],
    "defect_rate": ["scrap_rate", "reject_rate", "defect_pct", "failure_rate"],
    "scrap_units": ["defects", "rejected_units", "scrap_qty", "waste", "failed_units"],
    "downtime_hours": ["unplanned_downtime", "machine_downtime", "idle_time", "stop_hours", "breakdown_time"],
    "oee_score": ["overall_equipment_effectiveness", "efficiency", "utilization_pct", "performance_score"],
    "maintenance_hours": ["repair_time", "planned_downtime", "pm_hours", "maintenance_time"],
    "energy_consumption_kwh": ["power_usage", "electricity_kwh", "energy_used", "kwh"],
    "safety_incidents": ["accidents", "near_misses", "osha_recordables", "incidents"],
    "days_without_incident": ["safe_days", "days_since_accident"],
}

def normalize_string(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower())

def infer_data_profile(series):
    if pd.api.types.is_numeric_dtype(series): return "numeric"
    if pd.api.types.is_datetime64_any_dtype(series) or "date" in str(series.name).lower(): return "datetime"
    if series.nunique() < 50: return "categorical"
    return "text"

def infer_from_values(series):
    if series.dtype == 'object' or series.dtype.name == 'category':
        sample = series.dropna().astype(str).head(100)
        if not sample.empty:
            if sample.str.contains(r"HUB|DC|WH|WAREHOUSE|CENTER", case=False, regex=True).mean() > 0.4:
                return "logistics_location"
    return "unknown"

def run_schema_inference(df):
    print("🧠 Initiating Evidence-Based Semantic Schema Inference...")
    schema_mapping = {}
    evidence_log = []
    
    for original_col in df.columns:
        norm_col = normalize_string(original_col)
        mapped_to = None
        confidence = 0.0
        evidence = []

        # Layer 1: Exact Match
        for standard_name, aliases in UNIVERSAL_SCHEMA.items():
            if norm_col == normalize_string(standard_name) or norm_col in aliases:
                mapped_to = standard_name
                confidence = 1.0
                evidence.append("Exact normalized alias match")
                break
        
        # Layer 2: Value Pattern
        if not mapped_to:
            val_pattern = infer_from_values(df[original_col])
            if val_pattern == "logistics_location":
                if any(x in norm_col for x in ["src", "orig", "from", "start"]):
                    mapped_to = "source_name"
                    confidence = 0.95
                    evidence.extend(["Value Pattern: Logistics Location", "Name Context: Origin indicator"])
                elif any(x in norm_col for x in ["dest", "to", "end"]):
                    mapped_to = "destination_name"
                    confidence = 0.95
                    evidence.extend(["Value Pattern: Logistics Location", "Name Context: Destination indicator"])

        # Layer 3: Fuzzy Match
        if not mapped_to:
            all_known_terms = {alias: std for std, aliases in UNIVERSAL_SCHEMA.items() for alias in aliases}
            for std in UNIVERSAL_SCHEMA.keys(): all_known_terms[normalize_string(std)] = std
            
            matches = difflib.get_close_matches(norm_col, all_known_terms.keys(), n=1, cutoff=0.85)
            if matches:
                matched_alias = matches[0]
                proposed_std = all_known_terms[matched_alias]
                ratio = difflib.SequenceMatcher(None, norm_col, matched_alias).ratio()
                
                col_profile = infer_data_profile(df[original_col])
                numeric_metrics = ['revenue', 'total_cost', 'actual_duration_hours', 'total_weight', 'detention_minutes', 'temperature_celsius', 'asset_utilization_pct', 'actual_distance_miles']
                
                if proposed_std in numeric_metrics and col_profile != "numeric":
                    evidence.append(f"Fuzzy match rejected: `{original_col}` is {col_profile}, requires numeric.")
                else:
                    mapped_to = proposed_std
                    confidence = round(ratio, 2)
                    evidence.extend([f"Fuzzy Match: '{matched_alias}'", f"Profile Verified: {col_profile}"])

        if mapped_to and confidence >= 0.85:
            schema_mapping[original_col] = mapped_to
            evidence_log.append({"column": original_col, "mapped_to": mapped_to, "confidence": confidence, "evidence": evidence})

    for log in evidence_log:
        print(f"🎯 AI Mapped: `{log['column']}` -> `{log['mapped_to']}` | Conf: {log['confidence']} | Evidence: {log['evidence']}")
        
    df.rename(columns=schema_mapping, inplace=True)
    return df

def universal_clean(df):
    print("⚙️ Running universal data engineering layers...")
    df = run_schema_inference(df)
    
    initial_shape = df.shape[0]
    df = df.drop_duplicates()
    if initial_shape != df.shape[0]: print(f"🧹 Dropped {initial_shape - df.shape[0]} duplicate rows.")
        
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        if df[col].isnull().sum() > 0: df[col] = df[col].fillna(df[col].median())
            
    for col in df.columns:
        if 'date' in col.lower() or 'time' in col.lower() or 'timestamp' in col.lower():
            try: df[col] = pd.to_datetime(df[col])
            except: pass
            
    return df
