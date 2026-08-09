import os
import sys
import importlib

# Bootstrapper import
import bootstrap

def run_preflight_check():
    print("🔍 Running Architecture Pre-Flight Check...\n")
    has_errors = False

    # List of critical modules to test
    modules_to_test = [
        "utils.cleaner",
        "utils.profiler",
        "utils.kpi_engine",
        "utils.kpi_helpers",
        "utils.categorical_analysis",
        "utils.governance_engine",
        "utils.prompt_engine",
        "utils.llm_router",
        "utils.master_orchestrator",
        "industries.banking.pipeline",
        "industries.ecommerce.pipeline",
        "industries.finance.pipeline",
        "industries.hr.pipeline",
        "industries.logistics.pipeline",
        "industries.manufacturing.pipeline",
        "industries.pharma.pipeline",
        "industries.retail.pipeline",
        "evaluation.evaluation_engine",
        "evaluation.scorecard",
        "evaluation.benchmark_runner",
    ]

    for mod in modules_to_test:
        try:
            importlib.import_module(mod)
            print(f"  ✓ Import OK: {mod}")
        except Exception as e:
            print(f"  ❌ Import FAILED: {mod} --> Error: {e}")
            has_errors = True

    print("\n" + ("=" * 50))
    if has_errors:
        print("❌ Pre-flight check failed! Fix the reported import errors above.")
        sys.exit(1)
    else:
        print("✅ Pre-flight check passed! All pipeline modules and imports are verified.")
        sys.exit(0)

if __name__ == "__main__":
    run_preflight_check()
