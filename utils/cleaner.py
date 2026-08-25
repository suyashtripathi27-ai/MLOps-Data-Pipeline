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
    inner_filename = ""
    
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path, sep=None, engine='python', encoding='utf-8-sig')
        inner_filename = os.path.basename(file_path)
        
    elif file_path.endswith('.zip'):
        print(f"📦 Inspecting ZIP archive for Star Schema...")
        with zipfile.ZipFile(file_path, 'r') as z:
            csv_files = [f for f in z.namelist() if f.endswith('.csv') and not f.startswith('__MACOSX')]
            if not csv_files: raise ValueError("No CSV files found in ZIP.")
            
            if len(csv_files) == 1:
                target_file = csv_files[0]
                with z.open(target_file) as f: df = pd.read_csv(f, sep=None, engine='python', encoding='utf-8-sig')
                inner_filename = target_file
            else:
                core_keywords = ['trip', 'load', 'delivery', 'order', 'sales', 'pharmacy', 'pharma', 'otc']
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
                            dim_dfs[f_name.replace('.csv', '').split('/')[-1]] = pd.read_csv(f, sep=None, engine='python', encoding='utf-8-sig')
                            
                df = enrich_fact_table(fact_df, dim_dfs)
                inner_filename = target_file
                
    elif file_path.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(file_path)
        inner_filename = os.path.basename(file_path)
    else:
        raise ValueError("❌ Unsupported file format.")
        
    df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
    df = df.loc[:, ~df.columns.duplicated()].copy()
    
    # Attach inner filename metadata to DataFrame
    df.attrs['inner_filename'] = inner_filename
    
    print(f"🧹 Base load complete. Initial Shape: {df.shape}")
    return df

# ==========================================
# 🧠 THE EVIDENCE-BASED SEMANTIC ENGINE
# ==========================================
UNIVERSAL_SCHEMA = {
    # Core Financials & Banking
    "revenue": ["rev", "totalrevenue", "income", "sales", "triprevenue", "freightrevenue", "billedamount", "grossrevenue", "statvalue", "amt", "amount"],
    "total_cost": ["cost", "totalexpenses", "tripcost", "overallcost", "freightcost", "carrierfee", "invoicetotal"],
    "profit": ["netprofit", "netincome", "earnings", "netearnings", "profitamount"],
    "expense": ["expenses", "opex", "operatingexpense", "operating_expense", "operatingexpenses"],
    "assets": ["totalassets", "assettotal", "asset_value", "assetvalue"],
    "equity": ["shareholders_equity", "shareholderequity", "owner_equity", "ownersequity"],
    "current_assets": ["currentassets", "currassets", "currentasset", "currentassetstotal"],
    "current_liabilities": ["currentliabilities", "currliabilities", "currentliab", "currentliabs"],
    "cash": ["cashbalance", "cashamount", "cashonhand"],
    "operating_cashflow": ["cashfromoperations", "opcf", "operatingcf"],
    "investing_cashflow": ["cashfrominvesting", "invcf", "investingcf"],
    "financing_cashflow": ["cashfromfinancing", "fincf", "financingcf"],
    "investment_value": ["portfolio_value", "market_value", "investmentamount"],
    "return": ["roi", "pct_return", "investment_return"],
    "account_id": ["account_number", "acct_id", "acct_num", "account id", "Account No"],
    "transaction_date": ["date", "posting_date", "txn_date", "transaction date"],
    "balance": ["account_balance", "ending_balance", "available_balance", "ledger_balance"],
    "customer_id": ["customer_code", "cust_id", "client_id"],
    "loan_status": ["status", "payment_status", "loan_state", "load_status"],
    "outstanding_balance": ["loan_balance", "remaining_balance", "principal_remaining"],
    "fees_charged": ["fee_amount", "charges", "fee", "service_charge"],
    "aml_flag": ["aml_alert", "suspicious_flag", "fraud_flag", "is_suspicious"],
    "kyc_status": ["kyc_verified", "verification_status", "is_verified"],
    "default_flag": ["defaulted", "is_default", "loan_default"],
    "credit_score": ["fico_score", "cibil_score", "credit_rating", "bureau_score", "risk_score"],
    "interest_rate": ["apr", "lending_rate", "coupon_rate", "rate_pct", "interest_pct"],
    "cogs": ["cost_of_goods_sold", "cost_of_sales", "direct_costs", "cost_of_revenue"],
    "ebitda": ["operating_profit", "earnings_before_interest_taxes", "gross_operating_profit"],
    "accounts_receivable": ["ar", "receivables", "trade_debtors", "unpaid_invoices"],
    "accounts_payable": ["ap", "payables", "trade_creditors", "supplier_dues"],
    "ltv_ratio": ["loan_to_value", "ltv_pct"],
    "npa_status": ["non_performing_asset", "delinquency_status", "bad_loan"],
    "dti_ratio": ["debt_to_income", "dti"],
    "currency": ["ccy", "fx_currency", "base_currency", "local_currency"],
    "tax_amount": ["vat", "gst", "sales_tax", "tax_withheld", "tax_expense"],
    "collateral_value": ["asset_backing", "security_value", "pledged_amount"],

    # Logistics & Supply Chain
    "detention_minutes": ["detentiontime", "waittime", "facilitydelay", "dwelltime", "delaymins", "holdtime", "idletimehours", "detentionmins", "waitingtime"],
    "actual_duration_hours": ["transitdays", "shippingduration", "timeintransit", "leadtime", "actualtransittime", "deliverydays", "triptm"],
    "delay_flag": ["logisticsdelay", "delayoccurred", "isdelayed"],
    "source_name": ["originwarehouse", "facilityname", "originhub", "warehouse", "pickuplocation", "dispatchlocation", "shipperfacility", "srcwh"],
    "destination_name": ["destination", "deliverylocation", "consigneefacility", "dropoff", "finaldestination", "receivinghub", "destctr"],
    "actual_distance_miles": ["distance", "totaldistance", "tripmiles", "routedistance", "milesdriven"],
    "shipment_id": ["pronumber", "bolnumber", "trackingnumber", "loadid", "orderid", "sid", "referencenumber", "docketnumber"],
    "carrier_name": ["carrier", "scac", "transportcompany", "logisticsprovider", "truckingcompany"],
    "total_weight": ["weightkg", "weight", "payloadweight", "cargoweight", "grossweight", "netmass", "weightlbs"],
    "fuel_surcharge": ["fsc", "fuel_fee", "fuel_cost_adjustment"],
    "pod_status": ["proof_of_delivery", "delivered_status", "delivery_confirmation", "signature_status"],
    "otif_flag": ["on_time_in_full", "perfect_order", "otif", "delivery_success"],
    "freight_class": ["nmfc", "class_code", "freight_tier"],
    "incoterms": ["terms_of_trade", "shipping_terms", "fob", "cif", "exw"],
    "customs_status": ["clearance_status", "duty_paid", "import_status", "tariff_code", "hs_code"],
    "equipment_type": ["container_type", "trailer_size", "reefer", "flatbed", "dry_van"],

    # Manufacturing & Production
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
    "asset_utilization_pct": ["assetutilization", "utilizationrate", "capacityused"],
    "cycle_time": ["process_time", "lead_time_per_unit", "machine_cycle", "tact_time"],
    "defect_target": ["pass/fail", "class", "target", "label", "status", "yield_flag", "is_defect"],
    "sensor_timestamp": ["time", "timestamp", "datetime", "date_recorded"],
    "sensor_id": ["sensor", "feature", "channel", "signal"],
    "wip_inventory": ["work_in_progress", "wip_stock", "semi_finished_goods", "wip"],
    "rework_hours": ["rework_time", "correction_hours", "repair_labor", "re_processing_time"],

    # Pharma & Clinical
    "batch_id": ["batch_no", "lot_number", "lot_id", "production_batch"],
    "product_name": ["drug_name", "medication", "compound", "asset"],
    "therapeutic_area": ["category", "drug_class", "indication", "disease_area"],
    "manufacturing_date": ["mfg_date", "production_date", "date_of_manufacture"],
    "expiry_date": ["exp_date", "expiration", "valid_until", "use_by"],
    "quantity_produced": ["yield", "batch_size", "units_manufactured"],
    "quality_pass_rate": ["purity_score", "qa_rate", "yield_percent", "qc_score"],
    "regulatory_status": ["status", "fda_status", "approval_status", "qa_status"],
    "enrolled": ["participants", "enrollment_count", "subjects"],
    "dropouts": ["dropout_count", "withdrawn", "lost_to_followup"],
    "sae_count": ["serious_adverse_events", "adverse_events", "ae_count"],
    "batch_yield": ["yield_percentage", "production_yield", "yield_rate"],
    "oos_rate": ["out_of_spec_rate", "deviations", "oos_count"],
    "rft_rate": ["right_first_time", "first_pass_yield", "rft"],
    "capa_count": ["corrective_actions", "preventive_actions", "capas"],
    "temperature_celsius": ["temperature", "ambienttemp", "tempc"],
    "cold_chain_breaches": ["temp_excursions", "cold_chain_events", "temperature_breach"],
    "submission_date": ["nda_submission", "filing_date"],
    "approval_date": ["fda_approval", "ema_approval"],
    "complaints": ["complaint_count", "adverse_reports", "customer_complaints"],
    "clinical_phase": ["trial_phase", "study_phase", "phase", "research_phase"],
    "api_concentration": ["active_ingredient_pct", "strength", "potency", "assay_value"],
    "pharmacovigilance_alerts": ["pv_alerts", "safety_signals", "drug_safety_events"],
    "route_of_administration": ["roa", "dosage_form", "delivery_method"],

    # Retail, E-Commerce & Inventory
    "inventory": ["stock_value", "stock", "inventory_value"],
    "forecast_demand": ["predicted_demand", "demand_forecast", "projected_sales"],
    "actual_demand": ["quantity_sold", "actual_sales"],
    "store_id": ["store_num", "location_id", "branch_id", "retail_store", "shop_id", "site_id"],
    "sku_code": ["sku", "item_code", "product_code", "barcode", "upc", "ean", "article_number"],
    "atv": ["average_transaction_value", "avg_ticket", "basket_size", "avg_order_value", "aov"],
    "upt": ["units_per_transaction", "items_per_basket", "basket_units", "items_per_ticket"],
    "footfall": ["store_traffic", "visitor_count", "walk_ins", "door_swings", "customer_traffic"],
    "shrinkage": ["shrink", "inventory_loss", "theft_loss", "spoilage", "unaccounted_stock"],
    "sell_through": ["str", "sell_through_rate", "sell_thru_pct", "clearance_rate"],
    "markdown_amount": ["discount_amount", "markdowns", "promo_discount", "price_reduction"],
    "ecommerce_order_id": ["web_order", "cart_id", "checkout_id", "online_order_number", "order_ref"],
    "cac": ["customer_acquisition_cost", "acquisition_cost", "cost_per_acquisition", "cpa"],
    "clv": ["customer_lifetime_value", "ltv", "lifetime_value"],
    "cart_abandonment": ["abandoned_carts", "abandonment_rate", "drop_off_rate"],
    "return_rate": ["refund_rate", "return_pct", "rma_rate", "return_percentage"],
    "roas": ["return_on_ad_spend", "ad_roi", "marketing_roi"],
    "website_sessions": ["visits", "web_traffic", "unique_visitors", "site_visits"],
    "bounce_rate": ["exit_rate", "bounces", "single_page_visits"],
    "conversion_rate": ["cvr", "conv_rate", "sales_conversion"],
    "device_type": ["platform", "mobile_vs_desktop", "os_version"],
    "traffic_source": ["referrer", "channel", "utm_source", "campaign_origin"],
    "payment_method": ["gateway", "card_type", "tender_type", "payment_processor"],

    # HR & Workforce Management
    "employee_id": ["emp_id", "staff_id", "worker_code", "personnel_number", "associate_id"],
    "hire_date": ["doj", "date_of_joining", "start_date", "employment_date", "onboarding_date"],
    "termination_date": ["dol", "date_of_leaving", "end_date", "exit_date", "resignation_date", "offboarding_date"],
    "department": ["dept", "business_unit", "cost_center", "team", "function"],
    "job_title": ["designation", "role", "position", "job_grade"],
    "base_salary": ["basic_pay", "gross_salary", "annual_ctc", "wage", "base_pay", "compensation"],
    "attrition_flag": ["is_terminated", "left_company", "attrition", "turnover_flag", "is_active"],
    "performance_rating": ["appraisal_score", "rating", "review_score", "kpi_score", "band"],
    "time_to_fill": ["time_to_hire", "hiring_duration", "recruitment_days", "tt_fill"],
    "leave_balance": ["pto_balance", "vacation_days", "sick_leave", "available_leaves"],
    "manager_id": ["supervisor_id", "reports_to", "line_manager"],
    "employment_type": ["contract_type", "full_time", "fte_status", "part_time", "contractor"],
    "training_hours": ["cpd_hours", "learning_hours", "course_duration"],
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
    mapped_targets = set()
    
    for original_col in df.columns:
        norm_col = normalize_string(original_col)
        mapped_to = None
        confidence = 0.0
        evidence = []

        for standard_name, aliases in UNIVERSAL_SCHEMA.items():
            if norm_col == normalize_string(standard_name) or norm_col in aliases:
                mapped_to = standard_name
                confidence = 1.0
                evidence.append("Exact normalized alias match")
                break
        
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
            if mapped_to not in mapped_targets:
                schema_mapping[original_col] = mapped_to
                mapped_targets.add(mapped_to)
                evidence_log.append({"column": original_col, "mapped_to": mapped_to, "confidence": confidence, "evidence": evidence})
            else:
                print(f"⚠️ Skipped mapping `{original_col}` to `{mapped_to}` (Target already used)")

    for log in evidence_log:
        print(f"🎯 Locally Mapped: `{log['column']}` -> `{log['mapped_to']}` | Conf: {log['confidence']} | Evidence: {log['evidence']}")
        
    df.rename(columns=schema_mapping, inplace=True)
    df = df.loc[:, ~df.columns.duplicated()].copy()
    
    return df

def convert_unix_timestamps(df):
    """Detects Unix epoch timestamps in numeric columns and converts them to standard datetime/durations."""
    for col in df.columns:
        if any(k in col.lower() for k in ['time', 'date', 'duration', 'timestamp']):
            if pd.api.types.is_numeric_dtype(df[col]):
                sample = df[col].dropna()
                if not sample.empty:
                    val = sample.iloc[0]
                    if val > 1_000_000_000:
                        try:
                            df[col] = pd.to_datetime(df[col], unit='s', errors='coerce')
                        except Exception:
                            pass
                    elif val > 10_000 and 'lead' not in col.lower():
                        try:
                            df[f"{col}_hours"] = (df[col] / 3600).round(2)
                        except Exception:
                            pass
    return df

def universal_clean(df):
    print("⚙️ Running universal data engineering layers...")
    df = run_schema_inference(df)
    df = convert_unix_timestamps(df)
    
    initial_shape = df.shape[0]
    df = df.drop_duplicates()
    if initial_shape != df.shape[0]: print(f"🧹 Dropped {initial_shape - df.shape[0]} duplicate rows.")
        
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        if df[col].isnull().any(): 
            df[col] = df[col].fillna(df[col].median())
            
    for col in df.columns:
        if 'date' in col.lower() or 'time' in col.lower() or 'timestamp' in col.lower():
            try: df[col] = pd.to_datetime(df[col])
            except: pass
            
    return df
