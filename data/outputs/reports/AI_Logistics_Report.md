### 📊 1. Executive Summary & Reliability
* **Data Reliability Score**: 70/100
* **Confidence Level**: Medium — High missing data in several columns (>20% empty) and extreme variance in `cargo_damage_cost` reduce confidence in aggregate financial figures.
* **System Warnings**:
  - High missing data detected (some columns > 20% empty).
  - `cargo_damage_cost` extreme variance: standard deviation heavily distorted relative to the mean.

### 📈 2. Key Performance Indicators

{INSERT_KPIS_HERE}

| KPI Category | Metric | Observed Value | Note |
|---|---|---|---|
| **Schedule Compliance** | On-Time Flag (True) | 227,881 / 409,826 (55.6%) | ~44% of events recorded as late |
| **Schedule Compliance** | Average Detention (min) | 91.60 min (std 68.65) | Wide spread; max 239 min |
| **Schedule Compliance** | avg delay (scheduled → actual) | ~1 hour 15 min | Derived from mean datetime difference |
| **Fleet Utilization** | Idle Time (hours) | Mean 14.0 (std 68.34) | Extreme outlier distortion flagged |
| **Fleet Utilization** | Fuel Gallons Used (trip) | Mean 221.92 gal (std 126.68) | High variance; max 611.9 gal |
| **Fleet Utilization** | Fuel Purchased (gal) | Mean 124.81 gal (std 42.44) | Max 200 gal |
| **Fleet Utilization** | Avg MPG | 6.50 (std 0.58) | Narrow range 5.5–7.5 |
| **Fleet Utilization** | Actual Distance (mi) | Mean 9,156.84 mi (std 677.99) | Max 24,614 mi |
| **Fleet Utilization** | Actual Duration (hrs) | Mean 1,430.92 (std 802.49) | Likely minutes converted; ~24 hrs avg |
| **Revenue & Cost** | Revenue (per load) | Mean $27,473 (std $10,096) | Max $45,000 |
| **Revenue & Cost** | Total Fuel Cost | Mean $486.38 (std $174.89) | Max $997.90 |
| **Revenue & Cost** | Accessorial Charges | Mean $351.32 (std $218.44) | Max $891.82 |
| **Revenue & Cost** | Fuel Surcharge | Mean $14.00 (std 0) | Fixed surcharge |
| **Cargo Integrity** | Cargo Damage Cost | Mean $27,473 (std $10,096) | Only 796 non-null records (0.19%) |
| **Cargo Integrity** | Claim Amount | Mean $14.00 (std NaN) | Only 796 non-null records |
| **Cargo Integrity** | Vehicle Damage Cost | Mean $14.75 (std NaN) | Only 796 non-null records |
| **Weight** | Average Weight (lbs) | 14,758 lbs (std 6,837) | Max 62,245 lbs |
| **Event Mix** | Pickup events | 204,913 (50.0%) | Other event type is Delivery |
| **Event Mix** | Facility type (top) | Cross-Dock: 163,801 occurrences | 40% of all events |
| **Booking** | Dedicated loads | 203,538 (49.7%) | Other booking types present |
| **Load Type** | Refrigerated (top) | 248,6 occurrences | Second most common |

### 🔍 3. Operational Interpretations (The "Why")

**Detention & On-Time Performance**
- With an average detention of ~92 minutes and an on-time rate of only 55.6%, drivers are spending significant time at facilities. Possible contributing factors may include high cross-dock volumes (163,801 events at cross-dock facilities), dock door congestion, or appointment scheduling gaps. The standard deviation of 68.65 minutes indicates detention is inconsistent across trips — some stops are very quick while others are prolonged.

**Fuel Economics & Idle Time**
- Fuel purchased (124.8 gal) is roughly half of fuel used per trip (221.9 gal), which suggests either external fuel sources (other cards/facilities) or a data capture gap. The idle time mean of 14 hours with a standard deviation of 68 hours is heavily skewed by outliers; this extreme variance suggests potential anomalies in how idle time is recorded (e.g., a small number of trips with days of idle time). Possible contributing factors may include long layovers, mechanical delays, or metering inconsistencies.

**Cargo Damage & Claims**
- Only 796 of 409,826 records (0.19%) have a `cargo_damage_cost` value. The mean of ~$27,473 with a standard deviation of ~$10,096 indicates that when damage occurs, it is costly. This extreme variance (as flagged by the system) means the average is heavily influenced by a few large-loss events. The fact that `claim_amount`, `incident_type`, `incident_id`, and `vehicle_damage_cost` also have only 796 non-null values confirms these are tied to the same incident records. Possible contributing factors may include specific routes, equipment types, or seasonal conditions associated with those incidents — but without incident-level detail, this remains speculative.

**Revenue vs. Cost Structure**
- Average revenue per load (~$27,473) is substantially higher than average total fuel cost (~$486) and accessorial charges (~$351), suggesting the business is fundamentally load-revenue driven rather than fuel-cost driven. The narrow fuel price range ($3.15–$5.00/gal) provides limited arbitrage opportunity. Possible contributing factors to margin pressure may include the high accessorial charge variance and detention-related soft costs not captured in fuel metrics.

### 🚀 4. Practical Action Plan

1. **Investigate Detention Root Causes** — Segment detention minutes by facility type, facility name, and dock door to identify which locations are driving the 92-minute average. Cross-dock facilities (163,801 events) are a natural first focus since they handle the highest volume and often have different dwell dynamics than standard docks.

2. **Clean and Validate the Damage/Cost Outliers** — With only 796 incident records but extreme variance, the operations team should audit those records to confirm they are correctly classified and attributed. A small number of misattributed high-cost records could be distorting the entire damage-cost KPI. Until validated, treat the mean damage cost figure as unreliable.

3. **Reconcile Fuel Purchased vs. Fuel Used** — The gap between 124.8 gal purchased and 221.9 gal used per trip is a clear data-quality signal. The team should cross-reference fuel card data with onboard fuel monitoring to determine whether the discrepancy reflects external fuel sources, missing transactions, or measurement methodology differences. This reconciliation is a prerequisite for any fuel-efficiency improvement initiative.

### Traceable KPIs
| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 💰 Fleet Economics | **Overall Profit Margin** | `84.19%` | *((Revenue - Cost) / Revenue) * 100* | ``revenue`, `total_cost`` | High | None |
| 🚨 Risk & Compliance | **Cargo Damage Incident Rate** | `0.06%` | *(Trips with Damage > 0 / Total Trips) * 100* | ``cargo_damage_cost`` | High | None |
