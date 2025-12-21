# Operational Performance ETL (Python → SQL Server)

## 🚀 Executive Summary (Non-Technical)

Automated ETL solution that consolidates monthly tracking spreadsheets into a single, reliable data source in SQL Server.

The process replaces manual file handling and repetitive database updates, ensuring clean, validated, and up-to-date operational data for reporting and analytics.

---

## 👥 Who Is This For

- Operations & Logistics Managers  
- Supply Chain & Planning Teams  
- Business Analysts  
- Data & BI teams consuming SQL Server data  

---

## 🎯 Problem Statement

Tracking information was delivered as multiple monthly Excel files stored on shared folders.

Data consolidation, validation, and database updates were performed manually, creating delays, inconsistencies, and risk of duplicated or outdated records.

There was no controlled ETL process to guarantee data quality or timely availability.

---

## 🧠 Solution Overview

A Python-based ETL pipeline was developed to automatically load monthly Excel files, standardize and validate the data, generate a consolidated CSV, and load the most recent records into SQL Server.

The solution enforces schema consistency, applies business filters, and performs efficient batch inserts into the database.

---

## 🔍 Before vs After

### Before
- Multiple monthly Excel files  
- Manual column cleanup and filtering  
- Manual CSV generation  
- Manual SQL inserts  
- High risk of errors and duplicates  

### After
- Automated Excel ingestion  
- Standardized and validated dataset  
- Programmatic CSV generation  
- Controlled SQL Server load  
- Repeatable and auditable ETL process  

---

## 🧩 Business Rules & Logic

- Monthly Excel files are loaded dynamically  
- Only approved columns are processed  
- Columns are sorted to enforce schema consistency  
- Data is concatenated into a single dataset  
- ISO week is derived from document date  
- Only recent weeks are loaded into SQL Server  
- Sensitive or unstable columns are excluded  
- SQL table is created automatically if missing  
- Bulk inserts are executed in controlled batches  

---

## 📦 Output & Deliverables

- Consolidated CSV file with cleaned tracking data  
- SQL Server table containing the latest operational records  
- Execution log file with load statistics and timestamps  

---

## 📊 Business Value

- Eliminates manual monthly consolidation work  
- Ensures consistent and trusted data in SQL Server  
- Reduces operational risk and human error  
- Enables faster access to data for BI and reporting  

---

## 📈 Results & Impact

- Data availability reduced from days to minutes  
- Manual handling steps reduced by 90%+  
- Reliable weekly refresh of operational data  
- Scalable process ready for additional months  

---

## 🛠 Tech Stack

- Python  
- pandas  
- pyodbc  
- SQL Server  
- Excel (openpyxl)  

---

## 👤 My Role

- ETL design and architecture  
- Data validation and transformation  
- Python development  
- SQL integration and optimization  
- Operational logging and control  
