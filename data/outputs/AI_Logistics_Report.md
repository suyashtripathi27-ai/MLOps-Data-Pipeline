### 📊 1. Executive Summary & Reliability  
* **Data Reliability Score:** 70/100  
* **Confidence Level:** Medium  
  - The score reflects moderate data quality with notable systemic issues.  
* **System Warnings:**  
  - Severe outlier detected in `[factor]` (max value exceeds 99th percentile).  
  - Severe outlier detected in `[segment_osrm_distance]` (max value exceeds 99th percentile).  
  - Severe outlier detected in `[segment_factor]` (max value exceeds 99th percentile).  

---

### 📈 2. Core Operational KPIs (The Facts)  
- **Average Transit Time:** 20.50 hours  
- **Trip Cutoff (Failure) Rate:** 81.97%  
- **Total Route Deviation:** -17.80% over planned OSRM distance  
- **Average Routing Factor:** 2.12  

---

### 🔍 3. Operational Interpretations (The "Why")  
- The **81.97% Trip Cutoff Rate** suggests frequent operational delays or early termination of trips, which could stem from unplanned stops, traffic, or resource constraints.  
- The **severe outliers in `segment_osrm_distance` and `segment_factor`** may indicate data capture errors for specific trips or route deviations during execution.  
- The **negative route deviation (-17.80%)** raises concerns about potential route truncation or suboptimal path selection, though this could also reflect measurement inconsistencies.  
- An **average Routing Factor of 2.12** implies trips took over twice the planned time/distance in some cases, potentially linked to traffic or inefficient routing patterns.  

*All observations are tentative and require further validation due to data reliability limitations.*  

---

### 🚀 4. Practical Action Plan  
1. **Validate data capture processes** for trips with extreme `segment_osrm_distance` or `segment_factor` values to identify and correct measurement errors.  
2. **Investigate root causes** of the high Trip Cutoff Rate (e.g., traffic, driver stops) through on-ground audits or real-time tracking analysis.  
3. **Re-evaluate route planning** using historical data to address deviations and optimize Routing Factor, ensuring alignment with actual travel patterns.
