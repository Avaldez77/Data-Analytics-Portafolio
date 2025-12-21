<img width="911" height="608" alt="image" src="https://github.com/user-attachments/assets/3431fdd3-1a03-4df7-8129-178669766e15" />

# Cutoff Performance Automation (Data Pipeline)

## 🚀 Executive Summary (Non-Technical)

This solution automates the evaluation and reporting of operational performance based on order creation timing.

It consolidates raw operational data, applies standardized business rules, identifies late vs on-time execution, and delivers a clean, validated dataset ready for analytics and executive reporting.

The automation replaces a fragmented, manual process with a reliable, repeatable pipeline that ensures consistency, accuracy, and traceability across reporting cycles.

---

## 👥 Who Is This For

- Operations Managers  
- Supply Chain & Logistics Teams  
- Regional or Country Operations Leads  
- Business Intelligence teams consuming SQL-based datasets  

---

## 🎯 Problem Statement

Operational performance tracking was:

- Highly manual and time-consuming  
- Dependent on multiple unaligned data sources  
- Prone to human error (cutoff times, ownership, status calculation)  
- Inconsistent across countries, groups, and reporting weeks  
- Not scalable for historical or rolling-week analysis  

This resulted in unreliable performance metrics and limited visibility into execution delays.

---

## 🧠 Solution Overview

A fully automated data pipeline was built to:

- Extract operational and buyer reference data  
- Normalize identifiers and timestamps  
- Apply standardized cutoff rules by group and country  
- Assign operational ownership when automated users are detected  
- Classify each record as **On Time** or **Late**  
- Persist results into a SQL Server table for analytics and dashboards  

The solution runs end-to-end with no manual intervention.

---

## 🔍 Before vs After

### Before
- Manual Excel manipulation  
- Hard-coded filters and formulas  
- No consistent cutoff logic  
- No historical control or week filtering  
- High dependency on specific users  

### After
- Automated, rule-driven processing  
- Centralized cutoff and ownership logic  
- Consistent status calculation  
- Rolling 10-week controlled loads  
- SQL-ready output for reporting tools  

---

## 🧩 Business Rules & Logic

- Only relevant order types are evaluated  
- Only operational weeks within the defined range are processed  
- Cutoff times are determined by:
  - Operational group  
  - Country-specific overrides  
- Orders created by automated users are reassigned to responsible owners  
- Status is calculated by comparing creation time vs cutoff time  
- Only validated, recent data is inserted into the database  
- All rules are centralized and easily maintainable  

---

## 📦 Output & Deliverables

- Clean CSV export for audit or offline review  
- Structured SQL Server table for BI consumption  
- Rolling-week dataset optimized for dashboards  
- Execution log with timing, volume, and load traceability  

---

## 📊 Business Value

- Eliminates manual reporting effort  
- Reduces operational risk and human error  
- Ensures consistent KPI measurement across regions  
- Enables faster decision-making with trusted data  
- Scales effortlessly as volume and complexity grow  

---

## 📈 Results & Impact

- Significant reduction in reporting time  
- Improved data accuracy and consistency  
- Clear accountability for operational delays  
- Reliable historical tracking for trend analysis  
- Strong foundation for Power BI or similar dashboards  

---

## 🛠 Tech Stack

- Python  
- Pandas & NumPy  
- SQL Server  
- ODBC  
- CSV & logging for traceability  

---

## 👤 My Role

- Designed the end-to-end automation architecture  
- Defined and implemented business rules  
- Built the data transformation and validation logic  
- Optimized SQL insertion performance  
- Ensured data quality, maintainability, and scalability  
- Delivered a production-ready solution aligned with business needs  
