### 📊 1. Executive Summary & Reliability
* **Data Reliability Score:** 70/100  
* **Confidence Level:** Medium – the score is moderate and there are several system warnings that may affect downstream analysis.  
* **System Warnings:**  
  * High missing data detected (Some columns > 20% empty).  
  * [cargo_damage_cost] Extreme variance: Standard deviation is heavily distorted relative to the mean.

{INSERT_KPIS_HERE}

### 🔍 3. Operational Interpretations (The "Why")
* **Missing Data Impact** – The presence of >20 % missing values in key columns (e.g., `scheduled_datetime`, `actual_datetime`, `fuel_purchase_id`) suggests that any KPI relying on those fields may be under‑reported or biased.  
* **Cargo Damage Cost Variability** – The extreme spread in `cargo_damage_cost` indicates that a small subset of incidents may be inflating the average cost. Possible contributing factors may include:  
  * Inconsistent reporting of damage severity across facilities.  
  * Occasional large‑value claims that are not representative of typical operations.  
* **Detention Minutes Distribution** – The mean detention time (~91 min) with a standard deviation of ~69 min shows that while most detentions are moderate, a tail of long detentions exists. This variance suggests potential anomalies in scheduling or gate‑handling processes at specific hubs.  
* **Fuel Cost and Usage** – The mean fuel purchase price (~$3.90/gal) and gallons used (~221 gal) are within expected ranges, but the high standard deviation in `fuel_surcharge` and `total_cost` may reflect irregular fuel pricing or billing errors.  
* **Route & Load Characteristics** – The median load weight (~125 lbs) and pieces (~14) are typical for refrigerated loads, yet the wide range in `actual_distance_miles` (min 0 to max 45 k miles) indicates that some trips are outliers, possibly due to mis‑entered data or exceptional long‑haul assignments.

### 🚀 4. Practical Action Plan
1. **Data Quality Audit** – Conduct a focused review of columns with >20 % missingness (e.g., `scheduled_datetime`, `actual_datetime`, `fuel_purchase_id`). Validate source feeds and implement automated checks to flag incomplete records before KPI calculation.  
2. **Damage Cost Standardization** – Create a standardized damage classification schema and enforce mandatory fields for incident reporting. Use this schema to re‑calculate `cargo_damage_cost` so that outliers are identified and investigated separately.  
3. **Detention Process Review** – Map detention events to specific hubs and drivers. For hubs with detention times >2 × the median, schedule a process walk‑through to identify bottlenecks (e.g., gate clearance, paperwork delays) and implement corrective actions such as pre‑arrival notifications or dedicated gate staff.

---

### Traceable KPIs
| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 💰 Fleet Economics | **Overall Profit Margin** | `84.19%` | *((Revenue - Cost) / Revenue) * 100* | ``revenue`, `total_cost`` | High | None |
| 🚨 Risk & Compliance | **Cargo Damage Incident Rate** | `0.06%` | *(Trips with Damage > 0 / Total Trips) * 100* | ``cargo_damage_cost`` | High | None |
