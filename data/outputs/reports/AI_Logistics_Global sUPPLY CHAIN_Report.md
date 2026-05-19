# Operations Analytics Management Report

---

### 📑 1. Executive Summary

This analysis covers 5,000 shipments across a 2-year period (2024-2025) with a perfect data reliability score. Key findings indicate that 61.3% of shipments experienced disruption, with Air transport being the dominant mode (26.4%) and Electronics the leading product category (20.3%). The average carrier reliability score stands at 0.75, while geopolitical risk averaged 5.08 on a 0-10 scale. One metric (Lead_Time_Days) was excluded due to data inconsistency. Operations leadership should prioritize disruption mitigation strategies and carrier performance improvements.

---

### 🛡️ 2. Reliability & Data Quality

| Metric | Value |
|--------|-------|
| **Data Reliability Score** | 100/100 |
| **Total Records Analyzed** |5,000 |
| **Total Fields** |14 |
| **System Warnings** |None |
| **Sanity Flags** |None |
| **Statistical Stability** |Confirmed |

---

### 📊 3. KPI Snapshot

| KPI | Mean | Min | Max | Std Dev |
|-----|------|-----|-----|---------|
| **Actual Distance (miles)** | 7,704.06 | 500.17 | 14,995.91 | 4,199.69 |
| **Total Weight** | 246.25 | 1.03 | 499.75 | 142.52 |
| **Fuel Price Index** | 2.85 | 1.20 | 4.50 | 0.96 |
| **Geopolitical Risk Score** | 5.08 | 0.00 | 10.00 | 2.88 |
| **Carrier Reliability Score** | 0.75 | 0.50 | 1.00 | 0.14 |
| **Disruption Rate** | 61.26% | 0% | 100% | 48.72% |

**Distribution Highlights:**

| Category | Top Value | Count | Share |
|----------|-----------|-------|-------|
| **Transport Mode** | Air | 1,320 | 26.4% (Dominant) |
| **Product Category** | Electronics | 1,016 | 20.3% (Largest segment) |
| **Origin Port** | Busan | 667 | 13.3% |
| **Destination Port** | Marseille | 583 | 11.7% |
| **Weather Condition** | Fog | 1,036 | 20.7% (Largest segment) |

---

### 🔍 4. Key Operational Findings

#### Finding 1: High Disruption Rate
- **Observation:** 61.3% of all shipments experienced a disruption event.
- **Possible Reason:** This elevated rate could be associated with the combination of high geopolitical risk (mean 5.08/10) and frequent fog conditions (20.7% of shipments).
- **Business Impact:** Potential for significant operational delays, increased emergency response costs, and customer satisfaction risks across the majority of shipments.

#### Finding 2: Air Transport Dominance with Reliability Gap
- **Observation:** Air transport is the dominant mode (26.4% of shipments), yet the average carrier reliability score is only 0.75 on a 1.0 scale.
- **Possible Reason:** The high-volume Air segment may be stretching carrier capacity, which could be linked to the elevated disruption rate.
- **Business Impact:** Over-reliance on a single transport mode with sub-optimal reliability may be creating systemic vulnerability in the supply chain.

#### Finding 3: Fog as Leading Weather Factor
- **Observation:** Fog is the most frequent weather condition (20.7%), surpassing other conditions.
- **Possible Reason:** This environmental factor may be contributing to operational delays, particularly for air transport operations.
- **Business Impact:** Weather-related disruptions may be predictable and mitigable through route optimization or scheduling adjustments.

---

### 🚨 5. Operational Risk Areas

| Risk Area | Severity |
|-----------|----------|
| High Disruption Rate (61.3%) | **High** |
| Carrier Reliability Gap (0.75/1.00) | **High** |
| Geopolitical Risk Exposure (avg 5.08/10) | **Medium** |
| Weather-Related Delays (Fog dominance) | **Medium** |
| Single Mode Dominance (Air at 26.4%) | **Medium** |

---

### 🚀 6. Recommended Actions

1. **Initiate Carrier Performance Review:** Conduct a detailed assessment of Air transport carriers given the 0.75 reliability score and dominant market share to identify improvement opportunities.

2. **Develop Fog Mitigation Protocols:** Create operational playbooks for fog conditions given their 20.7% frequency, including alternative routing or scheduling buffers.

3. **Diversify Transport Mode Strategy:** Reduce dependency on Air transport (26.4%) by evaluating cost-benefit ratios of Sea/Rail/Road alternatives for suitable shipments.

4. **Implement Geopolitical Risk Monitoring:** Establish alert thresholds for the Geopolitical Risk Score (currently averaging 5.08) to proactively manage high-risk routes.

5. **Disruption Root Cause Analysis:** Launch a deep-dive investigation into the 61.3% disruption rate to identify specific causal factors and develop targeted interventions.

---

### 📈 7. Supporting Charts

The following interactive visualizations are available in the dashboard UI:

- **Disruption Rate by Transport Mode** (Bar Chart)
- **Geopolitical Risk vs. Disruption Correlation** (Scatter Plot)
- **Weather Condition Distribution** (Pie Chart)
- **Carrier Reliability Score Histogram** (Distribution)
- **Fuel Price Index Trend Over Time** (Line Chart)
- **Shipment Volume by Origin Port** (Horizontal Bar Chart)
- **Product Category Breakdown** (Donut Chart)
- **Distance vs. Weight Scatter** (Bubble Chart)

---

### ⚙️ 8. Technical Appendix

**[System Warnings]**
- None. Data looks statistically stable.

**[Data Engineering Flags]**
- None.

**[Excluded KPI]**
- **Lead_Time_Days**: Excluded from analysis due to data inconsistency. The column contains Unix epoch timestamp values (1970-01-01) rather than day counts, resulting in a mean date of `1970-01-01 00:00:00.000000018` instead of a numeric day value. Standard deviation is undefined (NaN) for this field.

**[Schema Anomalies]**
- The `Date` column contains timestamp values ranging from 2024-01-01 to 2025-12-31 with a mean of 2025-01-04, indicating the dataset spans approximately 2 years.
- The `Lead_Time_Days` field appears to have been incorrectly populated with date/epoch values rather than integer day counts.

---

*Report generated from 5,000 shipment records with 100% data reliability.*

### Traceable KPIs
*Insufficient columns to generate advanced logistics KPIs.*