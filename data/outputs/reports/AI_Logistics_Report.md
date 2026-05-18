

###📊 1. Executive Summary & Reliability  
* **Data Reliability Score:** 70/100  
* **Confidence Level:** Medium  
* **System Warnings:**  
  - High missing data detected (Some columns > 20% empty)  
  - [cargo_damage_cost] Extreme variance: Standard deviation is heavily distorted relative to the mean  

{INSERT_KPIS_HERE}  

---

### 🔍 3. Operational Interpretations (The "Why")  
* Based on the facts and sanity flags, what are the *potential* root causes?  
  - **Possible contributing factors may include** data quality issues in columns with high missing values, which could skew statistical summaries (e.g., [cargo_damage_cost] variance).  
  - **This variance suggests potential anomalies in** the [cargo_damage_cost] metric, possibly due to inconsistent reporting or outliers in damage incidents.  
  - The high missing data rate may obscure true patterns in [fuel_purchase_id], [load_status], or [incident_type], limiting actionable insights.  

* Address the specific KPI categories provided in the data (e.g., Fleet Economics, Hub Intelligence, Route Efficiency, etc.):  
  - **Fleet Economics:** The [cargo_damage_cost] distortion could indicate underreported or overreported damage events, affecting cost analysis.  
  - **Hub Intelligence:** Missing data in [facility_id] or [location_city] might hinder hub performance evaluations.  
  - **Route Efficiency:** Incomplete [actual_duration_hours] or [actual_distance_miles] could misrepresent route performance metrics.  

---

### 🚀 4. Practical Action Plan  
1. **Prioritize data cleaning** for columns with >20% missing values (e.g., [facility_name], [incident_date]) to improve reliability of KPIs like [revenue] or [fuel_surcharge].  
2. **Investigate [cargo_damage_cost] outliers** by cross-referencing with [incident_id] or [description] to validate if extreme values align with known incidents.  
3. **Validate data collection protocols** for [fuel_purchase_id] and [load_status] to ensure consistency, especially given the high missing data rate.  

---  
{INSERT_KPIS_HERE}


### Traceable KPIs
| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 💰 Fleet Economics | **Overall Profit Margin** | `84.19%` | *((Revenue - Cost) / Revenue) * 100* | ``revenue`, `total_cost`` | High | None |
| 🚨 Risk & Compliance | **Cargo Damage Incident Rate** | `0.06%` | *(Trips with Damage > 0 / Total Trips) * 100* | ``cargo_damage_cost`` | High | None |
