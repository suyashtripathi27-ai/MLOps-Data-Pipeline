#!/usr/bin/env python3
"""
tests/run_fixtures.py

Regression runner for tests/fixtures/. Productionizes the ad hoc testing done
by hand throughout this project's development (the industry-classification
suite, the keyword-collision scanner, the KPI/confidence verification checks)
into something that runs the same way every time, without needing a live
Gemini/Groq/etc. API key.

Deliberately does NOT call run_<industry>_analysis() / the LLM report step —
this only tests the fully local, deterministic parts of the pipeline:
  1. detect_industry()      -- does this file land on the right industry?
  2. generate_dynamic_kpis() -- does the industry's KPI engine actually
                                 produce a reasonable number of KPIs, or does
                                 it silently crash/return near-nothing (the
                                 exact failure mode of the pharma
                                 confidence_for bug found earlier)?

Usage:
    python tests/run_fixtures.py            # skips fixtures that don't exist yet
    python tests/run_fixtures.py --strict   # fails if any manifest entry is missing
"""

import sys
import os
import json
import argparse
import importlib
import zipfile
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import bootstrap  # noqa: F401  (sets up package __init__.py files as the real pipeline expects)

from utils.cleaner import load_and_clean, universal_clean
from main import detect_industry

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
MANIFEST_PATH = os.path.join(FIXTURES_DIR, "manifest.json")

ROUTER_MAP = {
    "logistics":     "industries.logistics.pipeline",
    "retail":        "industries.retail.pipeline",
    "banking":       "industries.banking.pipeline",
    "pharma":        "industries.pharma.pipeline",
    "finance":       "industries.finance.pipeline",
    "manufacturing": "industries.manufacturing.pipeline",
    "ecommerce":     "industries.ecommerce.pipeline",
    "hr":            "industries.hr.pipeline",
}


def load_fixture_df(path):
    """Mirrors main.py's real loading path: load_and_clean + universal_clean,
    so classification sees exactly what the real pipeline would see."""
    df = load_and_clean(path)
    df = universal_clean(df)
    return df


def run_one(rel_path, expected, strict):
    full_path = os.path.join(FIXTURES_DIR, rel_path)

    if not os.path.exists(full_path):
        status = "FAIL" if strict else "SKIP"
        print(f"  {status:4s}  {rel_path:35s}  (fixture not yet provided)")
        return status

    try:
        df = load_fixture_df(full_path)
    except Exception as e:
        print(f"  FAIL  {rel_path:35s}  could not load file: {e}")
        return "FAIL"

    columns = df.columns.tolist()
    detected = detect_industry(columns, os.path.basename(rel_path))
    expected_industry = expected["expected_industry"]
    industry_ok = detected == expected_industry

    kpi_count = None
    kpi_ok = True
    if industry_ok and detected in ROUTER_MAP:
        try:
            mod = importlib.import_module(ROUTER_MAP[detected])
            kpis = mod.generate_dynamic_kpis(df)
            kpi_count = len(kpis)
            kpi_ok = kpi_count >= expected.get("min_kpis", 1)
        except Exception as e:
            kpi_count = f"CRASHED: {e}"
            kpi_ok = False

    passed = industry_ok and kpi_ok
    status = "PASS" if passed else "FAIL"

    detail = f"industry={detected}"
    if not industry_ok:
        detail += f" (expected {expected_industry})"
    if kpi_count is not None:
        detail += f", kpis={kpi_count}"
        if not kpi_ok:
            detail += f" (expected >= {expected.get('min_kpis', 1)})"

    print(f"  {status:4s}  {rel_path:35s}  {detail}")
    return status


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true",
                         help="Fail if any manifest entry's fixture file is missing, "
                              "instead of skipping it. Use once all fixtures are in place.")
    args = parser.parse_args()

    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)
    manifest.pop("_comment", None)

    print(f"Running {len(manifest)} fixture(s) from {FIXTURES_DIR}\n")

    results = {}
    for rel_path, expected in sorted(manifest.items()):
        results[rel_path] = run_one(rel_path, expected, args.strict)

    passed = sum(1 for r in results.values() if r == "PASS")
    failed = sum(1 for r in results.values() if r == "FAIL")
    skipped = sum(1 for r in results.values() if r == "SKIP")

    print(f"\n{passed} passed, {failed} failed, {skipped} skipped (not yet provided)")

    if failed > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
