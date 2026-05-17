### 📊 1. Executive Summary & Reliability
* **Data Reliability Score:** **70/100**  
* **Confidence Level:** **Medium** – the score is moderate and the dataset contains several severe outlier flags, which suggests the need for careful validation before making definitive decisions.  
* **System Warnings:**  
  1. **[factor] Severe outlier:** Max value far exceeds the 99th‑percentile.  
  2. **[segment_osrm_distance] Severe outlier:** Max value far exceeds the 99th‑percentile.  
  3. **[segment_factor] Severe outlier:** Max value far exceeds the 99th‑percentile.  

#### Key Performance Indicators (KPIs) extracted from the payload  

| KPI | Mean / Median | 25th pct | 75th pct | Min | Max | Std Dev |
|-----|---------------|----------|----------|-----|-----|---------|
| **Actual Distance to Destination** (unit unknown) | 961.26 | 161 | 1 634 | 20 | 7 898 | 1 037.01 |
| **Actual Time** (seconds) | 232.93 | 22 | 286 | 9 | 1 927 | 344.76 |
| **OSRM Time** (seconds) | 284.77 | 29.91 | 343.19 | 9.01 | 2 326.20 | 421.12 |
| **OSRM Distance** (unit unknown) | 2.12 | 1.60 | 2.21 | 0.144 | 77.39 | 1.72 |
| **Factor** (ratio of actual vs. OSRM) | 2.12 | 1.60 | 2.21 | -23.44* | 77.39 | 1.72 |
| **Segment Actual Time** (seconds) | 0.036 µs* | 0.020 µs | 0.040 µs | -23.44 | 574.25 | 4.85 |
| **Segment OSRM Time** (seconds) | 0.018 µs* | 0.011 µs | 0.022 µs | 0 | 1.611 µs | 4.85 |
| **Segment OSRM Distance** (unit) | 22.83 | 12.07 | 27.81 | 0 | 2 191.40 | 17.86 |
| **Segment Factor** | 2.22 | 1.35 | 2.25 | -23.44 | 574.25 | 4.85 |

\* Values displayed as Unix‑epoch fractions (≈ microseconds) – the extremely low numbers indicate that these fields are likely placeholders or data‑entry errors.  

### 🔍 3. Operational Interpretations (The “Why”)

| Observation | Possible contributing factors may include… |
|-------------|--------------------------------------------|
| **Wide spread in *Actual Distance* (20 – 7 898)** | • Routes with vastly different geographic scopes (local vs. cross‑state). <br>• Data‑entry errors or missing unit conversion for some trips. |
| **Large variance between *Actual Time* and *OSRM Time*** (median ratio ≈ 0.82, but max factor > 70) | • Traffic congestion, weather events, or road closures not captured by the routing engine. <br>• Manual detours or load‑specific constraints (e.g., heavy freight requiring slower speeds). |
| **Severe outliers in *factor*, *segment_osrm_distance*, *segment_factor*** | • Incorrectly recorded timestamps (e.g., default epoch values). <br>• Mis‑aligned segment identifiers causing aggregation of unrelated legs. |
| **Negative or near‑zero times in segment metrics** | • Placeholder values (e.g., 0 or epoch start) that were not filtered before analysis. <br>• Data ingestion scripts that failed to convert string timestamps to numeric seconds. |
| **High standard deviations for most metrics** | • Heterogeneous service types (FTL vs. LTL) mixed in a single view. <br>• Inconsistent measurement units across centers. |

### 🚀 4. Practical Action Plan

1. **Data Quality Clean‑up**
   * Flag and isolate rows where any of the following conditions hold:  
     - `factor` > 10 or < 0.1  
     - `segment_osrm_distance` > 1 000 (or any value beyond the 99th percentile).  
     - Timestamp fields (`od_start_time`, `od_end_time`, segment times) equal to the Unix epoch (1970‑01‑01) or showing microsecond‑scale values.  
   * Work with the data engineering team to trace these anomalies back to source systems (e.g., GPS logs, routing API) and correct unit conversions or missing values.

2. **Segment‑Level Validation**
   * Generate a lookup table mapping each `trip_uuid` to its constituent segments. Compare the sum of `segment_actual_time` and `segment_osrm_time` against the overall `actual_time` and `osrm_time`.  
   * Where discrepancies exceed a pre‑defined tolerance (e.g., 15 %), raise a ticket for manual review. This will surface mis‑linked segment records that drive the outlier flags.

3. **Operational Benchmarking & Alerts**
   * Create two operational dashboards:  
     - **SLA Dashboard** – tracks *Actual Time* vs. *Planned/OSRM Time* for each route type (FTL, LTL). Highlight trips where the ratio (`factor`) exceeds the 75th‑percentile threshold (≈ 2.25).  
     - **Route‑Efficiency Dashboard** – monitors *Actual Distance* vs. *OSRM Distance* and flags trips where distance deviation > 30 %.  
   * Set up automated alerts (e‑mail or Slack) for any new trip that triggers the outlier conditions identified above, enabling the operations team to intervene promptly (e.g., re‑dispatch, driver feedback).  

By first securing the data foundation, then validating segment consistency, and finally instituting real‑time monitoring, the operations team can reduce variability, pinpoint true performance issues, and improve overall logistic reliability.

### 📊 2. Core Operational KPIs (Traceable & Explainable)

| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ⏱️ SLA & Delivery | **Average Transit Time** | `20.50 hrs` | *Mean(od_end_time - trip_creation_time)* | `trip_creation_time`, `od_end_time` | High | None |
| ⏱️ SLA & Delivery | **Trip Cutoff Rate** | `81.97%` | *(True / Total Valid) * 100* | `is_cutoff` | High | None |
| 🗺️ Route Efficiency | **Total Route Deviation** | `-17.80%` | *((Actual - Planned) / Planned) * 100* | `actual_...`, `osrm_...` | High | None |
| 🗺️ Route Efficiency | **Average Routing Factor** | `2.12` | *Mean(factor)* | `factor` | High | Semantic definition ambiguous. |
| 🏢 Hub Intelligence | **Most Congested Hub** | `Helencha_ColnyDPP_D (West Bengal)` | *Max delay grouped by source* | `source_name` | High | 0.2% missing in `source_name` |
| 💸 Cost & Efficiency | **Total Wasted Mileage** | `0.2 units` | *Sum(Actual - OSRM) where Actual > OSRM* | `actual...`, `osrm...` | High | None |
