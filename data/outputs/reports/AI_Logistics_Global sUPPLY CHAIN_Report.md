### 📑 1. Executive Summary
- The shipment portfolio shows a **average distance of ~7,700 miles** and **average weight of ~246 lb**.  
- **Fuel price index** averages **2.85**, while **geopolitical risk** sits at **5.08** on the provided scale.  
- **Disruption occurrence** is high at **~61 %** of shipments, with an average **lead time of ~0.75 days**.  
- These figures suggest that long hauls, higher risk scores, and fuel cost levels may be linked to the elevated disruption rate.

---

### 🛡️ 2. Reliability & Data Quality  

| Metric | Status |
|--------|--------|
| Data Reliability Score | 100 / 100 (Excellent) |
| System Warnings & Sanity Flags | None reported |
| Row Count | 5,000 (complete) |
| Column Count | 14 (complete) |
| Exclusions | None (all metrics available) |

---

### 📊 3. KPI Snapshot  

| KPI | Value | Interpretation |
|-----|-------|----------------|
| **Average Shipment Distance (miles)** | 7,704 | Indicates long‑haul nature of most moves. |
| **Average Total Weight (lb)** | 246.3 | Typical load size across the dataset. |
| **Average Fuel Price Index** | 2.85 | Baseline cost driver for transport. |
| **Average Geopolitical Risk Score** | 5.08 | Mid‑range risk exposure across routes. |
| **Average Lead Time (days)** | 0.75 | Relatively short turnaround from dispatch to delivery. |
| **Disruption Occurrence Rate** | 61.3 % | Majority of shipments experienced a disruption event. |

---

### 🔍 4. Key Operational Findings  

1. **Observation:** Disruption occurred in **61 %** of shipments.  
   **Possible Reason:** Higher average geopolitical risk (5.08) and fuel price index (2.85) may be associated with operational interruptions.  
   **Business Impact:** Frequent disruptions can erode service reliability, increase cost recovery efforts, and strain carrier relationships.  

2. **Observation:** Mean shipment distance is **~7,700 miles**, well above the 25th percentile (4,036 mi) and below the 75th percentile (11,348 mi).  
   **Possible Reason:** Long‑distance routes may expose shipments to more variable weather conditions and regulatory environments.  
   **Business Impact:** Extended distances can elevate fuel consumption and exposure to risk events, potentially inflating total logistics cost.  

3. **Observation:** Average lead time is **0.75 days**, yet the disruption rate remains high.  
   **Possible Reason:** Short lead times may limit buffer capacity to absorb delays caused by weather (e.g., fog) or carrier reliability fluctuations.  
   **Business Impact:** Tight schedules combined with disruptions could increase expediting fees and customer dissatisfaction.

---

### 🚨 5. Operational Risk Areas  

| Risk Area | Severity |
|-----------|----------|
| High disruption frequency | High |
| Elevated geopolitical risk scores | Medium |
| Long haul distances increasing fuel exposure | Medium |
| Limited lead‑time buffers | Low |
| Weather‑related conditions (e.g., fog) | Low |

---

### 🚀 6. Recommended Actions  

1. **Segment routing by geopolitical risk** – prioritize lower‑risk corridors for time‑critical shipments.  
2. **Introduce a buffer policy** – add a modest lead‑time cushion (e.g., +0.5 days) for routes exceeding the 75th percentile distance.  
3. **Negotiate fuel surcharge clauses** with carriers tied to the Fuel Price Index to mitigate cost volatility.  
4. **Implement a disruption monitoring dashboard** that flags shipments where risk score > 7 or fuel index > 3.5 for proactive intervention.  
5. **Review carrier contracts** focusing on reliability scores; consider performance‑based incentives for carriers maintaining >0.9 reliability.

---

### 📈 7. Supporting Charts  

- **Distance Distribution Histogram** – visualizes shipment distance quartiles.  
- **Weight vs. Fuel Price Scatter Plot** – explores correlation between load size and fuel cost.  
- **Disruption Rate by Geopolitical Risk Score** – heat map of disruption frequency across risk levels.  
- **Lead Time Box Plot by Transport Mode** – compares schedule variability across modes.  
- **Weather Condition Impact Dashboard** – stacked bar of disruption occurrences by weather type.

---

### ⚙️ 8. Technical Appendix  
**System Warnings:** None.  
**Excluded KPIs:** *Metric X was excluded from analysis due to data inconsistency.* (No metrics required exclusion; all were usable.)  
**Schema Anomalies:** None detected.

### Traceable KPIs
*Insufficient columns to generate advanced logistics KPIs.*