# 0. BOOTSTRAPPER (MUST BE FIRST): Enforces path resolution & __init__.py generation
import bootstrap

import os
import sys
import importlib  
from openai import OpenAI

# 1. IMPORT UNIVERSAL UTILITIES
from utils.cleaner import load_and_clean, universal_clean
from utils.profiler import generate_payload
from utils.chart_engine import generate_industry_charts
from evaluation.benchmark_runner import run_benchmark

# 2. HIGH-AVAILABILITY CLIENT SETUP
# Deliberately NOT run at import time. Importing this module (e.g. to reuse
# detect_industry() or INDUSTRY_KEYWORDS elsewhere -- a demo app, a notebook,
# a test) must not require API keys or exit the process. This is only called
# from main() itself, right before it's actually needed.
def _initialize_clients():
    print("🔌 Initializing Multi-API Client Router...")
    clients = {}

    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        clients["gemini"] = OpenAI(
            api_key=gemini_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        clients["groq"] = OpenAI(
            api_key=groq_key,
            base_url="https://api.groq.com/openai/v1"
        )

    or_key = os.getenv("OPENROUTER_API_KEY")
    if or_key:
        clients["openrouter"] = OpenAI(
            api_key=or_key,
            base_url="https://openrouter.ai/api/v1"
        )

    hf_key = os.getenv("HUGGINGFACE_API_KEY")
    if hf_key:
        clients["huggingface"] = hf_key

    if not clients:
        print("❌ ERROR: No API keys found. Please set at least one API key.")
        sys.exit(1)

    return clients

# Per-industry column-name signal library used for fully LOCAL, deterministic
# industry classification. No dataset values — only column NAMES — ever factor
# into this decision, and none of it is sent to any external API.
INDUSTRY_KEYWORDS = {
    "pharma": [
        'fda', 'adverse_event', 'clinical', 'dosage', 'therapeutic', 'batch',
        'yield', 'gmp', 'deviation', 'shelf_life', 'expiry', 'trial',
        'regulatory', 'formulation', 'drug_class', 'active_ingredient',
        'ndc_code', 'pharmacovigilance', 'capa', 'form_483', 'warning_letter',
        'sops', 'sterility', 'titer', 'assay', 'placebo', 'blinded',
        'serialization', 'counterfeit', 'dsicsa', 'patent_cliff', 'biosimilar',
        'formulary', 'pbm', 'copay', 'api_concentration', 'route_of_administration',
        'clinical_phase', 'efficacy_score', 'sae_count', 'oos_rate',
        'cold_chain_breach', 'temperature_excursion', 'nda_submission'
    ],
    "hr": [
        'attrition', 'jobrole', 'maritalstatus', 'employee_id', 'tenure',
        'engagement_score', 'headcount', 'recruitment', 'performance_rating',
        'training_hours', 'fmla', 'eeoc', 'grievance', 'compa_ratio',
        'vesting', 'payroll', 'succession_planning', 'bench_strength',
        'time_to_fill', 'time_to_hire', 'exit_interview', 'enps',
        'absenteeism', 'presenteeism', 'onboarding', 'offboarding',
        'pto_balance', 'cost_per_hire', 'voluntary_leave', 'flight_risk',
        'base_salary', 'annual_ctc', 'sick_leave', 'date_of_joining', 'termination_date',
        'salary', 'join_date', 'performance_score'
    ],
    "ecommerce": [
        'cart', 'checkout', 'pageview', 'session', 'conversion_rate',
        'add_to_cart', 'bounce_rate', 'website', 'wishlist', 'cac',
        'cpa', 'roas', 'ctr', 'cpc', 'rma_number', 'reverse_logistics',
        'restock_fee', 'cart_abandonment', 'payment_gateway', 'affiliate',
        'retargeting', 'bopis', 'dropshipping', 'web_order', 'online_order_number',
        'customer_lifetime_value', 'clv', 'site_visits', 'unique_visitors',
        'utm_source', 'split_shipment', 'click_and_collect'
    ],
    "manufacturing": [
        'downtime', 'oee', 'scrap', 'defect_rate', 'production_volume',
        'machine_id', 'maintenance', 'throughput_rate', 'work_order',
        'takt_time', 'cycle_time', 'bottleneck', 'changeover', 'mtbf',
        'mttr', 'rework', 'first_pass_yield', 'rft', 'six_sigma',
        'calibration', 'kanban', 'bom', 'cogs', 'absorption', 'spindle_time',
        'production_line', 'assembly_line', 'scrap_units', 'rejected_units',
        'unplanned_downtime', 'energy_consumption_kwh', 'osha_recordables',
        'wip_inventory', 'work_in_progress', 'equipment_lifecycle'
    ],
    "logistics": [
        'demurrage', 'detention', 'freight', 'hub', 'osrm', 'route_id',
        'fleet', 'sla', 'carrier', 'shipment_id', 'delivery_time',
        'transit_time', 'waybill', 'awb', 'bol', 'otif', 'cross_docking',
        'ftl', 'ltl', 'fuel_surcharge', 'accessorial', 'deadhead',
        'hos', 'eld_compliance', 'geofencing', 'wms', 'routing', 'telematics',
        'drop_size', 'proof_of_delivery', 'pod_status', 'freight_class',
        'nmfc', 'incoterms', 'customs_status', 'tare_weight', 'payload_weight'
    ],
    "banking": [
        'balance', 'loan', 'deposit', 'branch', 'interest_rate',
        'credit_score', 'overdraft', 'npa', 'atm', 'ifsc', 'kyc',
        'npl_ratio', 'delinquency', 'charge_off', 'fico', 'ltv', 'dti',
        'forbearance', 'sar', 'aml', 'structuring', 'chargeback',
        'nim', 'yield_curve', 'repricing', 'ddos', 'account_balance',
        'ledger_balance', 'cibil_score', 'non_performing_asset', 
        'loan_to_value', 'suspicious_flag', 'pep_status', 'euribor', 'poutcome',
        'upb', 'lien_status', 'balloon', 'neg_am', 'fed_guarantee',
        'prepay_penalty', 'ami_hud'
    ],
    "finance": [
        'cashflow', 'ebitda', 'balance_sheet', 'expense_category',
        'budget_variance', 'roi', 'npv', 'liquidity_ratio', 'gross_margin',
        'dscr', 'burn_rate', 'runway', 'receivables', 'payables',
        'dso', 'dpo', 'solvency', 'forex', 'hedging', 'derivatives',
        'mark_to_market', 'wacc', 'gearing', 'dividend_yield',
        'operating_profit', 'accounts_receivable', 'accounts_payable',
        'shareholders_equity', 'current_liabilities', 'operating_cashflow',
        'capital_expenditure', 'capex', 'opex', 'amortization'
    ],
    "retail": [
        'store', 'boxes_shipped', 'sales_person', 'footfall', 'markdown',
        'shrinkage', 'pos_terminal', 'sku', 'discount_pct', 'department',
        'atv', 'upt', 'gmroi', 'sell_through', 'planogram', 'dead_stock',
        'lfl', 'dwell_time', 'omnichannel', 'endless_aisle', 'visual_merchandising',
        'cannibalization', 'msrp', 'loss_leader', 'store_num', 'shop_id',
        'average_transaction_value', 'units_per_transaction', 'inventory_loss',
        'clearance_rate', 'markdown_amount', 'comp_sales', 'private_label'
    ],
}

# Fallback signal set used only when NOTHING above matched at all — picks the
# safest general-purpose landing spot from broad table shape. Deliberately uses
# specific compound terms rather than bare common English words (e.g. "order_id"
# not "order") — a bare word like "order" false-triggers on ordinary prose like
# "in order of preference" in a survey question header, which has nothing to do
# with a sales order.
GENERIC_SALES_SIGNALS = [
    'product', 'revenue', 'amount', 'unit_price', 'quantity', 'boxes', 
    'order_id', 'order_date', 'order_number', 'customer_id', 'sales',
    'subtotal', 'invoice_id', 'invoice_number', 'transaction_id', 
    'billing_address', 'shipping_address', 'payment_status', 'line_item', 
    'total_tax', 'grand_total', 'receipt_number', 'purchase_date',
    'item_code', 'item_description', 'qty_sold', 'gross_sales', 'net_sales',
    'discount_applied', 'sales_rep', 'vendor_id', 'supplier_id'
]


# 3. PROCESSED-FILE TRACKING (prevents re-analyzing unchanged datasets on every run)
import hashlib
import json

MANIFEST_PATH = "data/outputs/logs/.processed_manifest.json"


def _file_hash(file_path):
    """Content hash (not just filename/mtime) so re-uploading the same file
    is skipped, but a genuinely edited file with the same name is reprocessed."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_manifest():
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_manifest(manifest):
    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def detect_industry(columns_list, file_name=""):
    """
    FULLY LOCAL, DETERMINISTIC INDUSTRY ROUTER.

    No AI call happens here, and no dataset values (row content) are ever
    inspected or transmitted for this decision — only the column NAMES already
    in memory. Every dataset that reaches this pipeline gets classified purely
    by this system's own logic, scored against a curated per-industry keyword
    library. Ties/near-misses fall back deterministically to the closest
    general-purpose industry rather than guessing.

    Every low-confidence outcome (a single weak keyword match, or no match at
    all) is logged to CLASSIFICATION_REVIEW_LOG for later human review — this
    turns every ambiguous real-world dataset into a candidate for expanding
    INDUSTRY_KEYWORDS, the same way every bug found by hand this project was
    found: by noticing a dataset that didn't confidently match anything.
    """
    print(f"🔍 Sniffing data schema locally: {columns_list}")
    cols_str = str(columns_list).lower()
    fname_str = str(file_name).lower()

    scores = {}
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in cols_str)
        if industry in fname_str:
            score += 1  # small filename-hint tiebreaker
        scores[industry] = score

    best_industry = max(scores, key=scores.get)
    best_score = scores[best_industry]

    # A single coincidental keyword hit (e.g. "deposit" inside "Fixed_Deposits" on
    # an investment-preference survey, not an actual bank account record) is too
    # weak to commit to an operationally-strict industry. Real datasets for these
    # industries consistently produce multiple independent matches; a lone hit is
    # more often a false positive than a genuine signal.
    MIN_CONFIDENT_SCORE = 2
    if best_score >= MIN_CONFIDENT_SCORE:
        print(f"🎯 Classified as [{best_industry.upper()}] via local schema scoring "
              f"({best_score} operational column signal(s) matched)")
        return best_industry
    if best_score == 1:
        print(f"⚠️ Only a single weak signal for [{best_industry.upper()}] "
              f"(possible false positive) — treating as no strong match.")
        _log_classification_for_review(columns_list, file_name, scores,
                                         "weak_signal", best_industry)

    # No industry-specific operational evidence anywhere in the schema.
    # Fall back to the safest generic landing spot based on general table shape.
    if any(kw in cols_str for kw in ['cart', 'checkout', 'pageview']):
        print("🎯 No strong industry signal — defaulting to [ECOMMERCE] (cart/checkout shape)")
        _log_classification_for_review(columns_list, file_name, scores,
                                         "no_signal_fallback", "ecommerce")
        return "ecommerce"
    if any(kw in cols_str for kw in GENERIC_SALES_SIGNALS):
        print("🎯 No strong industry signal — defaulting to [RETAIL] (generic sales/transaction shape)")
        _log_classification_for_review(columns_list, file_name, scores,
                                         "no_signal_fallback", "retail")
        return "retail"

    print("⚠️ No industry signal detected at all in the schema — defaulting to [FINANCE]")
    _log_classification_for_review(columns_list, file_name, scores,
                                     "no_signal_hardcoded_default", "finance")
    return "finance"


CLASSIFICATION_REVIEW_LOG = "data/outputs/logs/classification_review_log.jsonl"


def _log_classification_for_review(columns_list, file_name, scores, reason, landed_on):
    """
    Append-only, human-reviewed learning loop. Never changes runtime behavior
    by itself — it only records that this run's classification was uncertain,
    why, and what every industry scored. Review this file periodically (see
    scripts/review_classification_log.py) and use real, recurring patterns in
    it to add new entries to INDUSTRY_KEYWORDS deliberately, the same way every
    keyword added this project came from a real dataset that didn't classify
    confidently the first time.
    """
    import json
    from datetime import datetime, timezone

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "file_name": file_name,
        "columns": columns_list,
        "scores": scores,
        "reason": reason,
        "landed_on": landed_on,
    }
    try:
        os.makedirs(os.path.dirname(CLASSIFICATION_REVIEW_LOG), exist_ok=True)
        with open(CLASSIFICATION_REVIEW_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError as e:
        print(f"⚠️ Could not write to classification review log: {e}")



def is_valid_executive_report(report_text: str) -> bool:
    """Validates that a report is a full executive analysis and not a system error message."""
    if not report_text or len(report_text.strip()) < 300:
        return False
    if "System Error" in report_text or "Failed to process" in report_text:
        return False
    return True

def main():
    print("🚀 Starting Universal Enterprise Pipeline...")

    clients = _initialize_clients()

    raw_dir = 'data/raw/'
    if not os.path.exists(raw_dir):
        print(f"❌ Error: Directory '{raw_dir}' not found.")
        sys.exit(1)

    output_dir = 'data/outputs/reports/'
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs('data/outputs/charts/', exist_ok=True)
    os.makedirs('data/outputs/logs/', exist_ok=True)

    processed_any_file = False
    manifest = _load_manifest()

    for file_name in os.listdir(raw_dir):
        if file_name.startswith('.') or file_name.lower() == 'process':
            continue
            
        if not file_name.endswith(('.csv', '.zip', '.xls', '.xlsx')):
            continue

        file_path = os.path.join(raw_dir, file_name)

        # ⏭️ SKIP FILES ALREADY ANALYZED (same content, already has a saved report)
        current_hash = _file_hash(file_path)
        if manifest.get(file_name) == current_hash:
            print(f"⏭️  Skipping {file_name} — already analyzed, content unchanged.")
            continue

        print(f"\n🚀 Processing dataset: {file_name}")
        processed_any_file = True
        
        try:
            df = load_and_clean(file_path)
            df = universal_clean(df)
        except Exception as e:
            print(f"❌ Error processing {file_name}: {e}")
            continue 
        
        columns = df.columns.tolist()
        
        # 🔒 ROUTING IS FULLY LOCAL — no data leaves the system for this step
        industry = detect_industry(columns, file_name)
        
        # 📊 Auto-Generate Charts & Embed Markdown
        chart_markdown = generate_industry_charts(df, industry, file_name)
        
        payload = generate_payload(df, industry_context=industry)
        payload["chart_markdown"] = chart_markdown
        
        print(f"🔀 Routing to {industry} module...")
        
        ROUTER_MAP = {
            "logistics":     ("industries.logistics.pipeline",     "run_logistics_analysis"),
            "retail":        ("industries.retail.pipeline",        "run_retail_analysis"),
            "banking":       ("industries.banking.pipeline",       "run_banking_analysis"),
            "pharma":        ("industries.pharma.pipeline",        "run_pharma_analysis"),
            "finance":       ("industries.finance.pipeline",       "run_finance_analysis"),
            "manufacturing": ("industries.manufacturing.pipeline", "run_manufacturing_analysis"),
            "ecommerce":     ("industries.ecommerce.pipeline",     "run_ecommerce_analysis"),
            "hr":            ("industries.hr.pipeline",            "run_hr_analysis")
        }

        if industry in ROUTER_MAP:
            mod_path, func_name = ROUTER_MAP[industry]
            try:
                module = importlib.import_module(mod_path)
                analysis_func = getattr(module, func_name)
                final_report = analysis_func(payload, clients, df)
            except Exception as e:
                print(f"❌ Failed to run pipeline for {industry}: {e}")
                log_file = f"data/outputs/logs/error_{os.path.splitext(file_name)[0]}.log"
                with open(log_file, "w", encoding="utf-8") as f:
                    f.write(f"Pipeline error for {industry}: {e}")
                continue 
        else:
            print(f"⚠️ Unmapped industry: {industry}. Skipping evaluation.")
            continue
            
        # Attach Chart Blocks to Markdown if not present
        if chart_markdown and chart_markdown not in final_report:
            if "# 2. Operational Risk Synthesis" in final_report:
                final_report = final_report.replace("# 2. Operational Risk Synthesis", f"{chart_markdown}\n# 2. Operational Risk Synthesis")
            else:
                final_report = final_report + f"\n\n{chart_markdown}"

        base_name = os.path.splitext(file_name)[0]
        report_name = f"AI_{industry.capitalize()}_{base_name}_Report.md"
        output_path = os.path.join(output_dir, report_name) 
        
        if is_valid_executive_report(final_report):
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(final_report)
                print(f"✅ Report saved to: {output_path}")
                
                # 🚀 V3 DYNAMIC EVALUATION TIER
                run_benchmark(dataset_path=file_path, version="v3", override_industry=industry)

                # ✅ Mark as processed only after a full successful run
                manifest[file_name] = current_hash
                _save_manifest(manifest)
                
            except Exception as e:
                print(f"❌ Failed to save report or run evaluation: {e}")
        else:
            print(f"⚠️ Generated report for {file_name} was invalid or incomplete. Skipping benchmark evaluation.")

    if not processed_any_file:
        print("\n⏸️ No valid data files found in data/raw/. Pipeline sleeping safely.")

if __name__ == "__main__":
    main()
