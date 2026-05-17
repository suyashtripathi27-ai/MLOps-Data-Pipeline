### 📊 1. Executive Summary & Reliability

* **Data Reliability Score:** 70/100
* **Confidence Level:** Medium (due to significant data quality issues)
* **System Warnings:**
  * **[factor]** Severe outlier: Max value (77.39) significantly exceeds the 99th percentile
  * **[segment_osrm_distance]** Severe outlier: Max value (2,191.4 km) significantly exceeds the 99th percentile
  * **[segment_factor]** Severe outlier: Max value (574.25) significantly exceeds the 99th percentile; also contains negative values (min: -23.44)

---

### 📈 2. Observed KPI Facts

| KPI Metric | Mean | Median (50%) | Std Dev | Min | Max | Interpretation |
|------------|------|--------------|---------|-----|-----|-----------------|
| **start_scan_to_end_scan** | 961 min (~16 hrs) | 449 min (~7.5 hrs) | 1,037 min | 20 min | 7,898 min (~5.5 days) | High variance suggests inconsistent delivery cycles |
| **cutoff_factor** | 232.93 | 66 | 344.76 | 9 | 1,927 | Extreme spread; possible SLA pressure indicator |
| **actual_distance_to_destination** | 284.77 km | 78.53 km | 421.12 km | 9.01 km | 2,326.20 km | Long-tail distribution with severe outliers |
| **factor** (OSRM vs Actual) | 2.12x | 1.86x | 1.72x | 0.14x | 77.39x | On average, actual time is 2x longer than estimated |
| **segment_factor** | 2.22 | 1.68 | 4.85 | -23.44 | 574.25 | Contains anomalous negative values; extreme positive outliers |

**Key Categorical Facts:**
* **is_cutoff = True:** 118,749 records (82% of dataset)
* **route_type:** FTL = 99,660 trips (69%), LTL = remaining 31%
* **Data dates:** Spans 2018-09-12 to 2018-10-08 (~3 weeks)

---

### 🔍 3. Operational Interpretations (The "Why")

**A. SLA Compliance Pressure (cutoff_factor analysis)**
* **Observed Fact:** The median cutoff_factor is 66, but the mean is 232.93—indicating a right-skewed distribution where most trips meet cutoffs, but a significant tail experiences extreme delays.
* **Possible contributing factors may include:** High-volume FTL routes (69% of trips) facing capacity constraints, or last-mile destination accessibility issues causing multiplier spikes.
* **This variance suggests potential anomalies in** how cutoff windows are defined or how factor calculations handle edge cases.

**B. Route Efficiency Gaps (factor & segment_factor analysis)**
* **Observed Fact:** The overall factor averages 2.12x (actual vs. estimated time), with segment_factor showing even higher variance (std: 4.85) and negative values.
* **Possible contributing factors may include:** 
  * The negative segment_factor values (min: -23.44) indicate a data ingestion or calculation error—possibly inverted timestamps or segment misassignment.
  * The severe outliers in segment_osrm_distance (max: 2,191 km) suggest possible GPS anomalies or route segmentation errors.
* **This variance suggests potential anomalies in** the OSRM integration or in how multi-segment trips are being computed.

**C. Data Quality Concerns**
* **Observed Fact:** segment_osrm_time and segment_actual_time columns display epoch timestamps (1970-01-01), indicating a type conversion issue.
* **Possible contributing factors may include:** System-level timestamp parsing errors during data export.
* **This variance suggests potential anomalies in** the data pipeline that should be remediated before further analysis.

---

### 🚀 4. Practical Action Plan

1. **Investigate the Negative segment_factor Records**
   * *Why:* Negative factor values are logically impossible and indicate a data bug.
   * *Action:* Query all records where segment_factor < 0. Validate whether these correspond to specific route_types, source-destination pairs, or time periods. Fix the root calculation logic in the ETL layer.

2. **Cap or Filter Extreme Outliers in factor Columns**
   * *Why:* Max factor of 77x and segment_factor of 574x distort any statistical model or KPI reporting.
   * *Action:* Apply a practical upper bound (e.g., 95th or 99th percentile) for reporting purposes. Investigate whether these represent genuine edge cases (e.g., extreme weather, vehicle breakdown) or data errors.

3. **Reconcile the Timestamp Columns (segment_osrm_time, segment_actual_time)**
   * *Why:* Epoch timestamps (1970) are unusable for operational analysis.
   * *Action:* Verify the data type casting in the export process. Reprocess these columns to standard datetime format before using them in any time-based KPI calculations.

---

*Analyst Note: All financial impact estimates have been omitted per the strict causality rule, as the data does not contain cost variables.*