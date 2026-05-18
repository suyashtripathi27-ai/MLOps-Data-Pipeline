
### 📊 1. Executive Summary & Reliability
* **Data Reliability Score:** 70/100
* **Confidence Level:** Medium
* **System Warnings:** 
  * [weight_kg] Extreme variance: Standard deviation is heavily distorted relative to the mean.
  - [weight_kg] Severe outlier: Max value significantly exceeds the 99th percentile.
  - [total_cost] Severe outlier: Max value significantly exceeds the 99th percentile.

*Insufficient columns to generate advanced logistics KPIs.*

### 🔍 3. Operational Interpretations (The "Why")
* **Cost Efficiency:** The network exhibits significant cost volatility. The severe outlier in `total_cost` (max: $6,562.21) suggests a potential profit leak from mismanaged high-value or oversized shipments. The mean cost ($204.98) is likely skewed upward by these extremes, masking true operational efficiency.
* **Fleet & Load Management:** The `weight_kg` metric shows extreme variance (std: 124.97 kg vs. mean: 30.18 kg) and a severe outlier (max: 5,404.20 kg). This indicates potential safety risks, non-compliant loading, and severe inefficiencies in vehicle utilization. A single anomalous shipment could distort fleet planning and maintenance schedules.
* **Network Consistency:** The `transit_days` range (1–12 days) and `distance_miles` spread (101–2,499 miles) reveal inconsistent routing or service level agreements. The median transit time is 4 days, but the maximum of 12 days points to potential bottlenecks or unreliable carrier performance on certain lanes.
* **Data Integrity & Process Gaps:** The presence of extreme statistical outliers flags potential data capture errors or genuine operational anomalies (e.g., incorrect weight entry, special project shipments). These must be investigated to separate signal from noise.

### 🚀 4. Strategic Action Plan
1.  **Why:** To isolate and understand the root of extreme cost and weight anomalies that are distorting average performance metrics and potentially creating safety or financial risks.
    *   **Action:** Initiate a forensic audit of the top 1% of shipments by `total_cost` and `weight_kg`. Cross-reference with carrier invoices, warehouse loading logs, and shipment manifests to validate data accuracy and identify process breakdowns (e.g., misclassification, special handling fees, data entry errors).

2.  **Why:** To stabilize cost forecasting and improve fleet loading plans by removing the influence of statistical outliers.
    *   **Action:** Implement a Winsorizing or trimming protocol for `weight_kg` and `total_cost` at the 99th percentile for all future operational reporting and KPI calculations. This will provide a clearer view of typical performance and more reliable baselines for budgeting and capacity planning.

3.  **Why:** To address inconsistent transit times that may indicate unreliable carrier partnerships or inefficient hub routing on specific lanes.
    *   **Action:** Analyze `transit_days` by `origin_warehouse` and `destination` pairs. Identify the bottom 10% of lane-performance combinations (longest transit times). Engage with the responsible carriers for these specific routes to renegotiate service standards or explore alternative routing/hub strategies.