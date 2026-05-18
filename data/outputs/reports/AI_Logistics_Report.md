### 📊 1. Executive Summary & Reliability
* **Data Reliability Score:** 70/100
* **Confidence Level:** Medium (based on the reliability score and multiple system warnings)
* **System Warnings:** 
  - Severe outlier in [factor] metric: Max value significantly exceeds the 99th percentile
  - Severe outlier in [segment_osrm_distance] metric: Max value significantly exceeds the 99th percentile
  - Severe outlier in [segment_factor] metric: Max value significantly exceeds the 99th percentile

### 📊 2. Key Performance Indicators (KPIs)

**Trip Volume & Coverage:**
* Total Trips Analyzed: 144,867
* Dataset Period: September 12 - October 3, 2018
* Training Data Ratio: 72.4% (104,858/144,867)

**Time Performance:**
* Mean Actual Trip Time: 234 seconds (approx. 3.9 minutes)
* Median Actual Trip Time: 66 seconds (approx. 1.1 minutes)
* Mean Time Factor (Actual/Estimated): 2.12
* Median Time Factor: 1.86

**Distance Performance:**
* Mean Estimated Distance (OSRM): 285 km
* Median Estimated Distance (OSRM): 79 km

**Segment-Level Performance:**
* Mean Segment Actual Time: 23 seconds
* Mean Segment Distance: 23 km
* Mean Segment Factor (Actual/Estimated): 2.22

**Cutoff Operations:**
* Trips with Cutoff: 82% (118,749/144,867)
* Mean Cutoff Factor: 233

**Route Distribution:**
* Full Truck Load (FTL) Routes: 68.8% (99,660/144,867)
* Other Route Types: 31.2% (45,207/144,867)

**Top Corridor:**
* Most Active Route: IND000000ACB to Gurgaon_Bilaspur_HB (Haryana)

### 🔍 3. Operational Interpretations (The "Why")

* Based on the mean factor of 2.12, trips are taking, on average, more than double the estimated time. This variance suggests potential anomalies in the estimation algorithm or consistent operational challenges not accounted for in the routing models.

* The significant difference between mean actual time (234 seconds) and median actual time (66 seconds) indicates a right-skewed distribution with some very long trips affecting the average. Possible contributing factors may include traffic congestion, route deviations, or unexpected stops for certain shipments.

* The severe outlier in the factor metric (max value of 77.39) indicates that some trips experienced extreme delays compared to estimates. These extreme cases may warrant individual investigation to identify root causes.

* The segment factor (2.22) closely aligns with the overall trip factor (2.12), suggesting the delays are consistent across both segment and trip levels. This pattern may indicate systemic issues rather than isolated segment problems.

* The high cutoff rate (82%) combined with a mean cutoff factor of 233 suggests that many trips are experiencing significant delays relative to their planned schedules. Possible contributing factors may include insufficient buffer time in planning or unexpected operational challenges.

* The discrepancy between segment actual time (23 seconds) and segment OSRM time (2 seconds) may indicate that the OSRM model underestimates travel time for certain segments, particularly for longer routes.

### 🚀 4. Practical Action Plan

1. **Investigate Outlier Segments:**
   - Focus analysis on the specific routes and segments showing extreme factor values
   - Review GPS/telematics data for outlier trips to identify common patterns
   - Implement targeted monitoring for frequently problematic corridors

2. **Refine Estimation Models:**
   - Audit the OSRM algorithm's performance, particularly for routes with high factor discrepancies
   - Incorporate historical performance data to improve time estimates
   - Consider implementing adaptive estimation that accounts for time-of-day, day-of-week, and seasonal factors

3. **Improve Operational Controls:**
   - Review and potentially adjust cutoff thresholds based on actual performance data
   - Implement real-time monitoring for trips exceeding certain factor thresholds
   - Develop contingency plans for routes with historically poor on-time performance

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
