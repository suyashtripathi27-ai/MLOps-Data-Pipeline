
### 📊 1. Executive Summary & Reliability
* **Data Reliability Score:** 70/100
* **Confidence Level:** Medium (due to high missing data and extreme variance warnings)
* **System Warnings:** 
  - High missing data detected (Some columns > 20% empty)
  - [cargo_damage_cost] Extreme variance: Standard deviation is heavily distorted relative to the mean

| Metric | Value |
|--------|-------|
| Total Records | 409,826 |
| Average Detention Time | 91.6 minutes |
| Average Fuel Cost | $124.81 |
| Average Total Cost | $351.32 |
| Average Revenue | $2,023 |
| Average Operating Hours | 78.7 |

### 🔍 3. Operational Interpretations (The "Why")
* Based on the facts and sanity flags, what are the potential root causes?

**On-Time Performance & Detention Times:**  
The average detention time of 91.6 minutes (std dev: 68.7) indicates substantial variability in facility dwell times. Possible contributing factors may include inconsistent scheduling practices, capacity mismatches at facilities, or delays in loading/unloading operations.

**Cost Structure Analysis:**  
The revenue-to-cost ratio (~$2,023 revenue vs $351 total cost) appears healthy on average. However, the extreme variance in cargo_damage_cost (only 796 populated records) suggests this may be a specialized incident field rather than a routine cost, with a few high-severity events potentially skewing the aggregate statistics.

**Geographic Distribution:**  
The limited geographic spread (2 cities, 20 states) with coordinates centered around 36.88°N, -93.27°W suggests concentrated operations in the central US region.

### 🚀 4. Practical Action Plan
1. **Validate cargo_damage_cost data model** - Investigate whether the 796 populated records represent legitimate incident-only capture or a data pipeline issue. Consider implementing a binary incident flag for more reliable frequency analysis.

2. **Segment detention performance by facility** - With 50 unique facilities, analyze detention times per location to identify outliers. High-variance facilities may require process improvements or capacity adjustments.

3. **Review fuel cost efficiency by route/truck** - With 180 unique routes and 176,645 fuel purchase records, analyze fuel_cost per route and per truck to identify inefficient operations. Consider benchmarking against the median fuel cost of $124.81.


- *Insufficient columns to generate advanced logistics KPIs.*
