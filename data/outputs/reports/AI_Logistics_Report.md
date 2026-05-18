
### 📊 1. Executive Summary & Reliability
* **Data Reliability Score:** 70/100
* **Confidence Level:** Medium
* **System Warnings:** 
  * High missing data detected (Some columns > 20% empty).
  * `[cargo_damage_cost]` Extreme variance: Standard deviation is heavily distorted relative to the mean.

{INSERT_KPIS_HERE}

### 🔍 3. Operational Interpretations (The "Why")
* **Data Quality & Missing Values:** The high rate of missing data (>20% in several columns) suggests potential issues with data capture processes, system integration gaps, or inconsistent reporting protocols across facilities or carriers. This limits the reliability of any derived insights for those fields.
* **Cargo Damage Cost Anomaly:** The extreme variance in `[cargo_damage_cost]` (mean ~$14,759, but max ~$49,744 and a non-zero minimum) indicates a heavily right-skewed distribution. This *suggests potential anomalies in* claims processing, data entry errors for large claims, or a small number of very high-severity incidents driving the average. The presence of a `claim_amount` column with similar count issues (796 non-null vs 409,826 total rows) further supports that damage claims are a rare but highly variable event.
* **Detention Patterns:** The `[on_time_flag]` shows ~55.7% of records are `True` (227,881 out of 409,826). The mean detention time is ~91.6 minutes with a median of 88 minutes. This relatively high median detention, combined with a 44.3% "not on time" rate, *may indicate* systemic delays at facilities, potentially due to inefficient scheduling, yard congestion, or prolonged loading/unloading processes.
* **Route & Distance Metrics:** The `[actual_distance_miles]` has a mean of ~1,430 miles and a median of ~1,299 miles, suggesting a distribution with some very long-haul trips inflating the average. The `[actual_duration_hours]` mean is ~25 hours vs. a median of ~23 hours, consistent with this skew. The `[average_mpg]` is tightly distributed (mean 6.50, std 0.58), indicating relatively consistent vehicle fuel efficiency across the fleet.

### 🚀 4. Practical Action Plan
1.  **Prioritize Data Hygiene:** Immediately investigate the root cause of the >20% missing data in key operational columns (e.g., `facility_id`, `driver_id`, `truck_id`). This could involve auditing data entry interfaces, EDI feeds, or API integrations with carriers and facilities.
2.  **Deep-Dive on Cargo Damage:** Isolate the 796 records with non-null `[cargo_damage_cost]` and `[claim_amount]`. Analyze these by `facility_id`, `incident_type`, and `route_id` to identify if specific locations, routes, or cargo types are disproportionately responsible for the extreme variance. Validate the accuracy of the largest claims.
3.  **Analyze Detention Hotspots:** Segment `[detention_minutes]` and `[on_time_flag]` by `facility_id` and `facility_type` (e.g., Cross-Dock vs. Distribution Center). Identify facilities with consistently high median detention and low on-time performance to target for process review or operational improvements.

### Traceable KPIs
| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 💰 Fleet Economics | **Overall Profit Margin** | `84.19%` | *((Revenue - Cost) / Revenue) * 100* | ``revenue`, `total_cost`` | High | None |
| 🚨 Risk & Compliance | **Cargo Damage Incident Rate** | `0.06%` | *(Trips with Damage > 0 / Total Trips) * 100* | ``cargo_damage_cost`` | High | None |
