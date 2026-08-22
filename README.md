# MLOps Data Pipeline

**A zero-cost, serverless MLOps pipeline that turns raw CSV drops into AI-written executive reports — with automated industry detection, KPI generation, governance checks, and a built-in evaluation suite.**

Drop a dataset into `data/raw/`, push it to GitHub, and the pipeline does the rest: cleans the data, figures out which of 8 industries it belongs to, computes the right KPIs, generates a board-ready markdown report through a multi-provider LLM cascade, validates its own claims against the source data, renders charts, scores itself against a benchmark, and commits everything back to the repo. No servers, no paid infrastructure — it runs entirely on GitHub Actions' free tier and free-tier LLM APIs.

## Table of Contents
- [How It Works](#how-it-works)
- [Supported Industries](#supported-industries)
- [Repository Structure](#repository-structure)
- [Multi-LLM Fallback](#multi-llm-fallback)
- [Automated Evaluation Suite](#automated-evaluation-suite)
- [Running It](#running-it)
- [Extending the Pipeline](#extending-the-pipeline)
- [Design Principles](#design-principles)

## How It Works

**1. Trigger** — Any push that touches `data/raw/**`, or a manual `workflow_dispatch`, kicks off the `.github/workflows/pipeline.yml` GitHub Actions job on a fresh Ubuntu runner.

**2. Bootstrap & preflight** — `bootstrap.py` puts the project root on `sys.path` and auto-generates any missing `__init__.py` files so nested modules import cleanly. `scripts/preflight.py` then imports every pipeline, utility, and evaluation module to fail fast on a broken import before any AI credits are spent.

**3. Ingest & clean** — `main.py` walks `data/raw/`, and for each `.csv`/`.xlsx`/`.zip` file runs `utils/cleaner.py` to load and standardize it (encoding, headers, missing values).

**4. Industry routing** — `detect_industry()` first tries cheap, deterministic keyword heuristics against the column names (e.g. `attrition`/`jobrole` → HR, `osrm`/`freight` → Logistics). If nothing matches, it falls back to an LLM call that's given the filename, column list, *and* a small sample of actual row values, and asked to classify the dataset into one of 8 supported industries — this saves API calls on obvious datasets and improves accuracy on ambiguous ones.

**5. Industry-specific analysis** — The dataset is routed to that industry's `pipeline.py` (e.g. `industries/retail/pipeline.py`), which runs a set of specialized analysis modules (sales, inventory, pricing, seasonality, workforce, etc.) to compute dozens of KPIs, each tagged with its formula, source column(s), and a confidence rating.

**6. Report generation** — `utils/master_orchestrator.py` prioritizes the most significant signals, composes a 3-layer system prompt (universal consultant rules + industry-specific reasoning + strict formatting/evaluation constraints via `utils/prompt_engine.py`), and sends it through the LLM cascade (`utils/llm_router.py`) to produce a structured executive report: situation summary, risk synthesis, prioritized action items, strategic directives, and governance notes.

**7. Governance & validation** — `utils/governance_engine.py` checks the generated narrative against what the data can actually support, flags claims that rely on missing fields, and injects reliability warnings rather than letting the LLM hallucinate confidence it hasn't earned.

**8. Charts & assembly** — `utils/chart_engine.py` renders industry-appropriate visualizations (distributions, category share, etc.) to `data/outputs/charts/` and embeds them into the report. The final markdown is validated (`is_valid_executive_report`) and written to `data/outputs/reports/`.

**9. Self-evaluation** — Every successful report is immediately scored by `evaluation/benchmark_runner.py` against a 64-scenario reference matrix (see below), and the result is appended to `evaluation/results/` and `evaluation/results/dashboard.csv`.

**10. Delivery** — The workflow commits the new reports, charts, and evaluation telemetry back to `main`, so downstream tools (Power BI, dashboards, etc.) always see fresh, versioned output with zero human intervention.

## Supported Industries

| Industry | Analysis modules |
|---|---|
| Retail | sales, store, department, inventory, seasonality, pricing, customer, promotion, workforce |
| Logistics | route, fleet, hub, SLA, freight, IoT |
| Banking | account, balance, branch, compliance, customer, deposit, fee, loan |
| Pharma | adverse events, clinical trials, compliance, manufacturing, regulatory, sales, shelf life, supply chain, forecast, product performance |
| Finance | cashflow, expenses, forecasting, fraud, investment, liquidity, profitability, revenue, risk |
| Manufacturing | cost, demand, downtime, efficiency, energy, forecasting, inventory, maintenance, production, quality, safety, supply chain, workforce |
| E-commerce | cart, conversion, customer, fraud, inventory, order, pricing, product, promotion, retention, review, sales, traffic |
| HR | absenteeism, compensation, compliance, department, engagement, productivity, recruitment, training, workforce stability |

Each industry has its own `pipeline.py`, `system_prompt.txt`, and `prompt.txt` under `industries/<name>/`, so the AI's tone and domain vocabulary are tailored per vertical.

## Repository Structure

```
MLOps-Data-Pipeline/
├── main.py                      # Entry point: orchestrates the full pipeline run
├── bootstrap.py                 # Path resolution + auto __init__.py generation
├── scripts/
│   └── preflight.py             # Import-health check run before the pipeline
├── utils/
│   ├── cleaner.py                # Loading + universal data cleaning
│   ├── profiler.py                # Dataset payload/profile generation
│   ├── kpi_engine.py / kpi_helpers.py   # KPI computation & deduplication
│   ├── categorical_analysis.py   # Categorical/relationship signal detection
│   ├── relationship_detector.py
│   ├── insight_engine.py         # Signal prioritization for the LLM
│   ├── confidence_engine.py      # Confidence scoring for KPIs/claims
│   ├── governance_engine.py      # Validates AI claims against real data
│   ├── prompt_engine.py          # 3-layer system prompt composition
│   ├── universal_system_prompt.txt
│   ├── llm_router.py              # Multi-provider fallback cascade
│   ├── master_orchestrator.py    # Ties signals + prompt + LLM + governance together
│   ├── chart_engine.py            # Chart generation
│   └── report_cleaner.py         # Post-processes raw LLM output
├── industries/
│   └── <industry>/
│       ├── pipeline.py           # run_<industry>_analysis() entry point
│       ├── *_analysis.py         # One module per KPI domain
│       ├── system_prompt.txt     # Industry-specific consultant persona
│       └── prompt.txt
├── evaluation/
│   ├── build_suite.py            # Defines the 64-scenario reference matrix
│   ├── benchmark_runner.py       # Scores each generated report
│   ├── evaluation_engine.py
│   ├── scorecard.py               # 6-dimension scoring rubric
│   ├── configs/industry_vocabulary.json
│   └── results/                  # Per-run JSON scores + dashboard.csv
├── data/
│   ├── raw/                      # Drop new datasets here to trigger the pipeline
│   ├── processed/
│   └── outputs/
│       ├── reports/              # Generated executive markdown reports
│       └── charts/                # Generated PNG charts
└── .github/workflows/pipeline.yml
```

## Multi-LLM Fallback

Rather than depending on a single paid API, `utils/llm_router.py` cascades through free-tier providers in order, retrying transient failures and skipping instantly on rate limits:

1. **Gemini** (`gemini-2.5-flash`)
2. **Groq** (`llama-3.1-8b-instant`)
3. **OpenRouter** (`meta-llama/llama-3-8b-instruct:free`)
4. **Hugging Face Inference API** (`Mistral-7B-Instruct-v0.2`) as a last resort

The pipeline only requires *one* of these API keys to run — set as many as you have for better resilience. Keys are read from environment variables (`GEMINI_API_KEY`, `GROQ_API_KEY`, `OPENROUTER_API_KEY`, `HUGGINGFACE_API_KEY`).

## Automated Evaluation Suite

Every report the pipeline produces is immediately graded, not just generated. `evaluation/build_suite.py` defines a reference matrix of 64 industry × scenario combinations (8 industries × 8 risk scenarios each, e.g. retail → `store_performance_decline`, HR → `attrition_crisis`), each with an expected primary risk, secondary risks, recommended actions, and expected governance domains.

`evaluation/benchmark_runner.py` matches the incoming dataset to the closest scenario by filename/industry, then `evaluation/scorecard.py` scores the generated report (out of 60) across six dimensions:

- **Behavioral intelligence** — did it correctly identify the underlying risk pattern?
- **Prioritization** — are findings ranked by actual severity?
- **Recommendation traceability** — do recommendations trace back to specific data signals?
- **Governance** — did it correctly flag missing/unreliable data instead of overclaiming?
- **Executive readability** — is it written for a decision-maker, not a data scientist?
- **Industry realism** — does it use the right domain vocabulary and framing?

Results are logged per-run to `evaluation/results/v3/*.json` and rolled up in `evaluation/results/dashboard.csv`, giving a running quality trend across every dataset the pipeline has ever processed — useful for catching prompt or model regressions over time.

## Running It

**Automatically (recommended):** push a new `.csv`/`.xlsx`/`.zip` file into `data/raw/` on `main`. GitHub Actions handles everything else.

**Manually via GitHub:** open the Actions tab → *Run Master Orchestrator Pipeline* → *Run workflow*.

**Locally:**
```bash
pip install pandas numpy openpyxl openai matplotlib seaborn rapidfuzz google-generativeai tenacity pydantic

export GEMINI_API_KEY=...        # at least one of these four is required
export GROQ_API_KEY=...
export OPENROUTER_API_KEY=...
export HUGGINGFACE_API_KEY=...

python scripts/preflight.py      # optional but recommended: sanity-checks all imports
python evaluation/build_suite.py # builds/refreshes the evaluation reference matrix
python main.py                   # processes everything in data/raw/
```
Reports land in `data/outputs/reports/`, charts in `data/outputs/charts/`, and evaluation scores in `evaluation/results/`.

## Extending the Pipeline

To add a new industry (e.g. "Insurance"):
1. Create `industries/insurance/` with a `pipeline.py` exposing `run_insurance_analysis(payload, clients, df)`, plus `system_prompt.txt` and any `*_analysis.py` KPI modules you need.
2. Add `insurance` to the `supported_industries` list and `ROUTER_MAP` in `main.py`.
3. Add classification heuristics for it in `detect_industry()` if it has obviously distinctive columns.
4. Add its risk scenarios to the matrix in `evaluation/build_suite.py` so generated reports get benchmarked too.

## Design Principles

- **Zero-cost by default** — GitHub Actions free tier + free-tier LLM APIs; no servers to maintain.
- **Fault-tolerant** — an LLM inspects the schema before committing to a processing path, and a report is only saved/benchmarked if it passes a basic sanity check (`is_valid_executive_report`).
- **Self-grading** — the pipeline doesn't just generate reports, it scores its own output against a fixed rubric every time, so quality drift is visible in `dashboard.csv` rather than discovered by a human reading a bad report.
- **Governed, not just generated** — the governance engine actively pushes back on claims the data doesn't support, rather than letting the LLM sound confident about gaps.
- **Horizontally scalable** — new industries plug in by adding a folder and a router entry, without touching the core orchestration logic.
