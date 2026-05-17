### 📊 1. Executive Summary & Reliability
* **Data Reliability Score:** 70/100  
* **Confidence Level:** **Medium** – the score is above a neutral threshold but several severe outlier warnings reduce certainty.  
* **System Warnings:**  
  1. **[factor]** – Max value (1927) far exceeds the 99th‑percentile (≈286).  
  2. **[segment_osrm_distance]** – Max value (2191.4) far exceeds the 99th‑percentile (≈27.8).  
  3. **[segment_factor]** – Max value (574.25) far exceeds the 99th‑percentile (≈2.25).  

---  

#### Core KPIs (as reported in the statistical summary)

| KPI | Mean | Median (50 %) | 75 % | Max | Std Dev |
|-----|------|---------------|------|-----|---------|
| **Actual Distance to Destination** (units?) | 961.26 | 449 | 1 634 | 7 898 | 1 037.01 |
| **Factor** (ratio of actual vs. planned?) | 2.12 | 1.86 | 2.21 | 1 927 | 344.76 |
| **Segment Factor** (segment‑level ratio) | 2.22 | 1.68 | 2.25 | 574.25 | 4.85 |
| **Segment OSRM Distance** (planned distance) | 22.83 | 23.51 | 27.81 | 2 191.40 | 17.86 |
| **Segment OSRM Time** (planned time) | 0.144 h (≈8.6 min) | 0.136 h | 0.173 h | 0.003 h (≈0.18 s) | 1.72 h |
| **Actual Time** (total trip duration) | 234.07 h | 66.13 h | 286.71 h | 1 927.45 h | 344.99 h |
| **OSRM Time** (planned total time) | 284.77 h | 78.53 h | 343.19 h | 2 326.20 h | 421.12 h |

*Note: Units are taken directly from the payload; interpretation (km, minutes, etc.) is not assumed.*

---  

### 🔍 3. Operational Interpretations (The “Why”)

| Observation | Possible Contributing Factors (cautious language) |
|-------------|----------------------------------------------------|
| **Factor mean = 2.12, median ≈ 1.86, max = 1 927** | Possible contributing factors may include data entry errors, extreme route deviations, or occasional use of atypical transport modes that dramatically inflate the ratio. The presence of severe outliers suggests occasional trips where the actual distance or time is far larger than the OSRM‑planned benchmark. |
| **Segment OSRM Distance median ≈ 23.5 but max = 2 191** | This variance suggests potential anomalies in segment segmentation logic (e.g., splitting a long haul into a single “segment” rather than multiple). It may also reflect rare, very long cross‑regional legs that are not typical of the majority of routes. |
| **Segment Factor median ≈ 1.68, max = 574.25** | A very high segment factor could be driven by traffic incidents, road closures, or inaccurate OSRM estimates for certain road classes. It may also point to data quality issues where the planned distance was recorded incorrectly. |
| **Actual vs. OSRM Time disparity (mean ≈ 234 h vs. 285 h)** | The lower mean actual time relative to OSRM time could indicate that the routing engine is conservative (over‑estimating travel time) or that drivers are achieving higher speeds on average. Conversely, the large standard deviation implies that some trips experience far longer durations, possibly due to cut‑off handling (“is_cutoff” flag) or SLA pressures. |
| **High frequency of “training” in `trip_creation_time` column** | The dominant value (≈ 72 % of rows) labelled “training” may indicate that a large portion of the dataset represents simulated or test trips rather than live operations, which could skew the distributions of distance and factor. |

---  

### 🚀 4. Practical Action Plan

| Step | Action | Rationale (plain language) |
|------|--------|----------------------------|
| 1️⃣ | **Validate extreme outliers** – extract records where `factor` > 100, `segment_osrm_distance` > 500, or `segment_factor` > 50 and run a manual audit (check route logs, GPS traces, and data entry). | Removing or correcting a few erroneous rows will dramatically tighten the distributions and improve the reliability of any downstream analysis. |
| 2️⃣ | **Separate “training” trips from operational trips** – create a flag based on `trip_creation_time` or another identifier, and analyse the two subsets independently. | If the “training” subset is synthetic, mixing it with live data can mask true performance patterns and lead to misleading KPI baselines. |
| 3️⃣ | **Refine segment generation logic** – review how `segment_osrm_distance` and `segment_factor` are calculated, especially for long‑haul routes that currently appear as single segments with extreme values. Consider splitting routes longer than a configurable threshold (e.g., > 500 km) into multiple segments. | More granular segmentation will reduce the frequency of extreme segment‑level ratios and provide a clearer view of where inefficiencies occur. |

These steps are designed to be executable with existing data pipelines and to yield measurable improvements in KPI stability without requiring sophisticated modelling.

### 📊 2. Core Operational KPIs (Traceable & Explainable)

| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ⏱️ SLA & Delivery | **Average Transit Time** | `20.50 hrs` | *Mean(od_end_time - trip_creation_time)* | `trip_creation_time`, `od_end_time` | High | None |
| ⏱️ SLA & Delivery | **Trip Cutoff Rate** | `81.97%` | *(True / Total Valid) * 100* | `is_cutoff` | High | None |
| 🗺️ Route Efficiency | **Total Route Deviation** | `-17.80%` | *((Actual - Planned) / Planned) * 100* | `actual_...`, `osrm_...` | High | None |
| 🗺️ Route Efficiency | **Average Routing Factor** | `2.12` | *Mean(factor)* | `factor` | Medium | Severe outliers in `factor` Semantic definition ambiguous. |
| 🏢 Hub Intelligence | **Most Congested Hub** | `EXCLUDED` | *N/A* | Multiple | Low | Data failed minimum threshold validation (Epoch corruption suspected). |
| 🏢 Hub Intelligence | **Highest Cutoff Concentration** | `Gurgaon_Bilaspur_HB (Haryana) (22284 failures)` | *Count(Cutoff=True) by Source* | `source_name`, `is_cutoff` | High | None |
| 💸 Cost & Efficiency | **Average Excess Distance (per trip)** | `0.00 units` | *Mean(Actual Dist - OSRM Dist) where Actual > OSRM* | `actual...`, `osrm...` | High | None |
