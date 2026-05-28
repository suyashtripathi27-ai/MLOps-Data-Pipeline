### ⚠️ Pipeline Alert: All AI services are currently unavailable.

---
### 📊 Technical Appendix: Operational KPIs
| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 💳 Account Analysis | **Avg Account Balance** | `$76,485.89` | *Mean(Balance)* | ``balance`` | High | None |
| 💳 Account Analysis | **Min Account Balance** | `$0.00` | *Min(Balance)* | ``balance`` | High | None |
| ⚠️ Risk Exposure | **Accounts in Overdraft (Negative Balance)** | `0 (0.00%)` | *COUNT(balance < 0)* | ``balance`` | High | None |
| 💰 Balance & Liquidity | **Average Account Balance** | `$76,485.89` | *AVG(balance)* | ``balance`` | High | None |
| 💰 Balance & Liquidity | **Top 5% Account Concentration** | `11.6% of Total Deposits` | *SUM(Top 5% Balances) / SUM(All Balances)* | ``balance`` | High | None |
| 👥 Customer Analysis | **Total Customers** | `10000` | *Count(Distinct Customers)* | ``customer_id`` | High | None |
| 👥 Customer Analysis | **Avg Customer Balance** | `$76,485.89` | *Mean(Customer Total Balance)* | ``customer_id`, `balance`` | High | None |
| 👥 Customer Analysis | **Max Customer Balance** | `$250,898.09` | *Max(Customer Total Balance)* | ``customer_id`, `balance`` | High | None |
| 🏢 Branch Analysis | **Total Branches** | `3` | *Count(Distinct Branches)* | ``Geography`` | High | None |
| 🏢 Branch Analysis | **Avg Branch Revenue** | `$254,952,964.29` | *Mean(Branch Revenue)* | ``Geography`, `balance`` | High | None |
| 🏢 Branch Analysis | **Top 10 Branch Share** | `100.0%` | *(Sum of Top 10 / Total) * 100* | ``Geography`, `balance`` | High | None |
| 🛠️ System Diagnostics | **Excluded Metrics (1 Items)** | `EXCLUDED` | *N/A* | `Governance Engine` | Low | Affected Areas: [💳 Account Analysis] | Reason: Missing 'account_id' column. |
| 🛠️ System Diagnostics | **Excluded Metrics (1 Items)** | `EXCLUDED` | *N/A* | `Governance Engine` | Low | Affected Areas: [💳 Account Analysis] | Reason: Missing or invalid 'amount' column. |
| 🛠️ System Diagnostics | **Excluded Metrics (1 Items)** | `EXCLUDED` | *N/A* | `Governance Engine` | Low | Affected Areas: [💳 Account Analysis] | Reason: Requires valid 'date' and 'amount'. |
| 🛠️ System Diagnostics | **Excluded Metrics (1 Items)** | `EXCLUDED` | *N/A* | `Governance Engine` | Low | Affected Areas: [🏦 Deposit Analysis] | Reason: Requires 'product' and numeric 'amount'. |
| 🛠️ System Diagnostics | **Excluded Metrics (1 Items)** | `EXCLUDED` | *N/A* | `Governance Engine` | Low | Affected Areas: [🏦 Deposit Analysis] | Reason: Missing numeric 'interest' column. |
| 🛠️ System Diagnostics | **Excluded Metrics (1 Items)** | `EXCLUDED` | *N/A* | `Governance Engine` | Low | Affected Areas: [💰 Loan Analysis] | Reason: Missing numeric 'outstanding' column. |
| 🛠️ System Diagnostics | **Excluded Metrics (1 Items)** | `EXCLUDED` | *N/A* | `Governance Engine` | Low | Affected Areas: [💰 Loan Analysis] | Reason: Missing 'status' column. |
| 🛠️ System Diagnostics | **Excluded Metrics (1 Items)** | `EXCLUDED` | *N/A* | `Governance Engine` | Low | Affected Areas: [💰 Loan Analysis] | Reason: Missing numeric 'rate' column. |
| 🛠️ System Diagnostics | **Excluded Metrics (1 Items)** | `EXCLUDED` | *N/A* | `Governance Engine` | Low | Affected Areas: [👥 Customer Analysis] | Reason: Missing 'account_id'. |
| 🛠️ System Diagnostics | **Excluded Metrics (1 Items)** | `EXCLUDED` | *N/A* | `Governance Engine` | Low | Affected Areas: [👥 Customer Analysis] | Reason: Missing valid 'date'. |
| 🛠️ System Diagnostics | **Excluded Metrics (1 Items)** | `EXCLUDED` | *N/A* | `Governance Engine` | Low | Affected Areas: [💵 Fee Analysis] | Reason: Missing numeric 'fee' column. |
| 🛠️ System Diagnostics | **Excluded Metrics (1 Items)** | `EXCLUDED` | *N/A* | `Governance Engine` | Low | Affected Areas: [🛡️ Compliance Analysis] | Reason: Missing AML flag column. |
| 🛠️ System Diagnostics | **Excluded Metrics (1 Items)** | `EXCLUDED` | *N/A* | `Governance Engine` | Low | Affected Areas: [🛡️ Compliance Analysis] | Reason: Missing KYC status column. |
| 🛠️ System Diagnostics | **Excluded Metrics (1 Items)** | `EXCLUDED` | *N/A* | `Governance Engine` | Low | Affected Areas: [🛡️ Compliance Analysis] | Reason: Requires transaction flag and numeric amount. |
