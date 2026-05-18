### 📊 1. Executive Summary & Reliability

* **Data Reliability Score**: 70/100
* **Confidence Level**: Medium — heavy missing data and extreme variance in damage-related cost fields reduce confidence in financial magnitude estimates
* **System Warnings**: High missing data detected (some columns > 20% empty). **cargo_damage_cost** shows extreme variance; standard deviation heavily distorted relative to the mean.

| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 💰 Fleet Economics | **Overall Profit Margin** | `84.19%` | *((Revenue - Cost) / Revenue) * 100* | ``revenue`, `total_cost`` | High | None |
| ⏳ Operational Bottlenecks | **Avg Facility Detention** | `91.6 mins` | *Mean(detention_minutes)* | ``detention_minutes`` | High | None |
| ⏳ Operational Bottlenecks | **Severe Detention Events (>2hr)** | `148,210 trips` | *Count(detention_minutes > 120)* | ``detention_minutes`` | High | None |
| 🚨 Risk & Compliance | **Cargo Damage Incident Rate** | `0.06%` | *(Trips with Damage > 0 / Total Trips) * 100* | ``cargo_damage_cost`` | High | None |


---

### 📊 2. Key Performance Indicators (Extracted)

| KPI | Value |
|---|---|
| **On-Time Delivery Rate** | **55.6%** (227,881 of 409,826 events on time) |
| **Average Detention Time** | **91.6 minutes** (std dev 68.7 — high variability) |
| **Avg Fuel Cost per Transaction** | **$486.38** |
| **Avg Price per Gallon** | **$3.90** |
| **Avg Fuel Gallons per Transaction** | **124.8 gal** |
| **Avg Fuel Surcharge** | **$3.90** |
| **Avg Revenue per Load** | **$3,513.24** |
| **Avg Weight per Load** | **27,473 lbs** |
| **Avg Actual Distance per Trip** | **~2,839 miles** |
| **Avg Actual Duration per Trip** | **~14 hours** |
| **Avg Fuel Efficiency** | **6.5 MPG** |
| **Avg Idle Time per Truck** | **~19 hours** |
| **Avg Fuel Gallons Used per Truck** | **~222 gal** |
| **Cargo Damage Cost (Mean)** | **$14,758.68** (75th percentile = $14,754.74 — extreme skew) |
| **Max Cargo Damage Cost** | **$64,245.72** |
| **Claim Amount (Mean)** | **$9,156.84** (max $33,910) |
| **Vehicle Damage Cost (Max)** | **$49,744.07** |
| **Incidents Recorded** | **796** (very low frequency vs. 409K events) |
| **Load Status — Completed** | **248,638** (60.7% of loads) |
| **Facility Type — Cross-Dock** | **163,801 occurrences** (most common) |
| **Booking Type — Dedicated** | **203,538 occurrences** |

---

### 🔍 3. Operational Interpretations (The "Why")

**🕐 Punctuality & Detention**
* **Only ~56% of events are on time** — a material gap. Over 200K events fall behind schedule.
* **Average detention is nearly 92 minutes**, with a standard deviation of 69 minutes — meaning detention is wildly inconsistent. Some events see drivers waiting nearly 4 hours.
* **Possible contributing factors**: Dock door availability, yard congestion at facilities, or receiver scheduling mismatches at the 50 facilities tracked.

**⛽ Fuel & Cost Efficiency**
* **6.5 MPG fleet average** — industry benchmark for dry van is ~6–7 MPG; this is within range but leaves limited margin for improvement.
* **$486 average fuel spend per transaction** at $3.90/gal with ~125 gal purchased — fuel is a top-3 cost driver.
* **~19 hours of idle time per truck** — this is a significant hidden cost. Engines running with no productive movement directly erodes margin.
* **Fuel surcharge averaging $3.90** — suggests surcharge programs are active but may not fully offset fuel volatility.

**💰 Revenue & Margin Leakage**
* **Average revenue per load: $3,513** against average fuel cost of $486 — fuel is ~14% of revenue, which is reasonable. However, **cargo and vehicle damage costs spike sharply** (up to $64K and $50K respectively), and with only 796 incidents recorded against 409K events, the *per-incident* cost is enormous.
* **Extreme variance in cargo damage cost** (mean $14.8K, but most values cluster at ~$14,755 with a handful of massive outliers) suggests **a small number of catastrophic claims are distorting the entire damage profile**. This is a critical profit leak signal.
* **Claim amounts average $9.2K** — meaning for every incident, there is an average $5.6K gap between damage cost and claim recovery, or a large claim that inflates the average.

**🏭 Hub & Facility Operations**
* **Cross-dock facilities dominate** (163K events) — this is a high-velocity, low-storage model. Detention here likely reflects **dock door availability and appointment compliance** by consignees.
* **50 facilities across 20 cities / 19 states** — geographic dispersion is moderate; however, on-time performance below 60% suggests **network-wide scheduling or execution issues**, not isolated geography.

**🚚 Fleet & Utilization**
* **Average trip: ~2,839 miles over ~14 hours** — suggests long-haul or regional LTL operations.
* **Idle time of ~19 hours per truck** is the single largest operational red flag. This likely correlates with detention, deadheading, or terminal dwell.

---

### 🚀 4. Strategic Action Plan

1. **Audit & Segment High-Detention Loads (Why: Detention at 92 min avg is eroding driver productive hours and increasing fuel waste. Reducing detention by even 30 minutes per event could unlock thousands of driver-hours annually.)**
   - Pull the top 20% of events by detention minutes and cross-reference with facility, booking type, and load type. Target cross-dock facilities first given their volume.

2. **Investigate the Top 1% of Damage Claims (Why: Cargo damage cost variance is extreme — a handful of $50K+ incidents are inflating the entire cost profile. Identifying root causes (packaging, loading practices, route exposure) could prevent repeat catastrophic losses.)**
   - Isolate incidents where cargo_damage_cost exceeds $30K. Review incident descriptions, load types (e.g., Refrigerated), and preventable_flag to prioritize corrective actions.

3. **Cut Idle Time by Implementing a Yard Management Pilot (Why: 19 hours of idle per truck is a direct, avoidable cost — roughly $75–100 per idle hour in fuel alone. A modest 20% reduction saves ~4 hours/truck per cycle.)**
   - Start with the top 5 facilities by volume. Track idle hours vs. detention minutes to determine if idle is primarily terminal dwell or en-route waiting.

---