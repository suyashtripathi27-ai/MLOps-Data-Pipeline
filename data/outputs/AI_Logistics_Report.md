### 📊 1. Executive Summary & Reliability

* **Data Reliability Score**: 70/100
* **Confidence Level**: Medium — large dataset (144K rows) but three severe outlier flags reduce confidence in summary-level averages and max-based KPIs.
* **System Warnings**: Three severe outlier flags on `[factor]`, `[segment_osrm_distance]`, and `[segment_factor]` — max values significantly exceed the 99th percentile.

---

### 📈 2. Key Performance Indicators (Extracted from Payload)

| KPI | Value | Interpretation |
|---|---|---|
| **Total Trips** | 144,867 | 104,858 labeled *training*, 39,? labeled *testing* (top: `training`) |
| **Route Type Split** | FTL: 99,660 (≈69%) · Other: 45,207 (≈31%) | FTL dominates the fleet |
| **Cutoff Rate** | 118,749 / 144,867 ≈ **82%** | ~82% of trips were flagged as `cutoff = True` |
| **Avg Actual Time to Destination** | 961 min (≈16 hrs) | Mean heavily skewed by outliers (max 7,898 min ≈ 5.5 days) |
| **Median Actual Time to Destination** | 449 min (≈7.5 hrs) | More representative central tendency |
| **Avg OSRM Time** | 1970-01-01 00:00:00.000000416 | Timestamp format; duration ~234 min (median 66 min) |
| **Avg Actual Distance to Destination** | 234 km | Mean skewed; median 66 km |
| **Avg OSRM Distance** | 285 km | Mean skewed; median 78.5 km |
| **Avg Segment Actual Time** | 22.8 min | Median 23.5 min |
| **Avg Segment OSRM Time** | 2.2 min | Median 1.68 min — **OSRM segment time is ~8–10× lower than actual segment time** |
| **Avg Factor** | 2.12 | Median 1.86; range 0.14 – 77.39 (severe outlier flagged) |
| **Avg Segment Factor** | 2.22 | Median 1.68; max 574.25 (severe outlier flagged) |
| **Actual Distance vs OSRM Distance** | 234 km vs 285 km | On average, OSRM overestimates distance by ~21% |
| **Longest Recorded Trip** | Actual time: 7,898 min (~5.5 days); Distance: 2,326 km | Likely an outlier or multi-leg consolidation |

---

### 🔍 3. Operational Interpretations (The "Why")

**Observed facts**:

1. **82% cutoff rate** — the overwhelming majority of trips were flagged as `cutoff = True`, suggesting the dataset captures predominantly trips that deviated from their planned OSRM route or schedule.
2. **OSRM vs Actual gap on segments** — segment-level OSRM time (2.2 min) is roughly 8–10× lower than segment actual time (22.8 min). This is a large discrepancy at the segment level.
3. **Distance overestimation by OSRM** — OSRM distance (285 km mean) exceeds actual distance (234 km mean) by ~21% on average.
4. **Severe outliers on `factor`, `segment_osrm_distance`, `segment_factor`** — max values (77.39, 574.25) far exceed the 99th percentile, meaning a small number of segments/trips are driving inflated averages.

**Possible contributing factors may include**:

- **Route planning vs. real-world execution**: The high cutoff rate (82%) suggests most trips did not follow the planned OSRM route. Possible contributing factors may include traffic disruptions, last-mile deviations, or unplanned stoppages that are not captured in the OSRM model.
- **Segment-level time inflation**: The ~10× gap between OSRM segment time and actual segment time could indicate that OSRM's shortest-path assumption does not account for real-world road conditions, checkpoints, or dwell time at intermediate points. This variance suggests potential anomalies in how segments are defined or timed.
- **Distance discrepancy**: OSRM overestimating distance relative to actual could stem from route detours being shorter than the planned path, or OSRM using road-network distances while actual follows more direct paths. This variance suggests potential anomalies in distance measurement methodology.
- **Outliers driving summary statistics**: The severe outlier flags mean that means (e.g., 961 min average trip time, 234 km average distance) are likely inflated. The median values (449 min, 66 km) are more operationally representative.

---

### 🚀 4. Practical Action Plan

1. **Filter and isolate outlier segments** — Pull the top 1% of rows by `segment_factor` and `segment_osrm_distance` to understand whether these correspond to specific origin-destination pairs, time-of-day windows, or route types. If a handful of OD pairs are skewing the dataset, they can be analyzed separately or excluded from model training.

2. **Validate the 82% cutoff rate** — Work with the operations team to confirm the business definition of `cutoff`. If it simply means "trip deviated from planned OSRM route," then the high rate is expected and the OSRM baseline may not be appropriate for this network. A practical step: recalculate KPIs on the **non-cutoff** subset (~18% of trips) to establish a cleaner baseline for route planning accuracy.

3. **Segment-level time audit** — The ~10× gap between OSRM segment time and actual segment time warrants a closer look. Pull a sample of high-factor segments and compare: (a) OSRM-recommended segment distance vs. actual, (b) actual speed vs. OSRM assumed speed. This will reveal whether the gap is due to slower-than-expected travel speeds, unplanned stops, or incorrect segment mapping.