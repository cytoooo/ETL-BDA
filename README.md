E-Commerce Data Pipeline & Analytics:
This project provides a complete end-to-end data pipeline using the Olist e-commerce dataset. It extracts raw CSV files, cleans the data, 
loads it into a SQLite data warehouse, runs automated data quality checks, and generates business analytics to track revenue growth, retention, and 
shipping performance.

Project Components:
Data Pipeline: Cleans missing data (e.g., filling 610 missing product categories) and builds the ecommerce_warehouse.db SQLite database.

Data Quality (DQ): Automated Python alerts that catch bad business logic, specifically designed to trigger an alarm on payment mismatches.

SQL Analytics: 5 SQL scripts calculating month-over-month revenue, top categories, rolling averages, repeat purchase rates, and shipping delays.

Metrics & Charts: Python scripts that generate visual charts (North Star and Guardrail metrics) for reporting.

Note: Some results have been documented in this repository

How to Run

Build the Data Warehouse
Run the main extraction and loading script to clean the data and create the database.
(elt_pipeline.py) 

Run Data Quality Checks
Audit the database for structural and financial errors. Expect this to intentionally fail and crash the pipeline to flag the broken rows.
(dq_checks.py)

Execute the Analytical SQL Reports
Run the automation script to execute all 5 .sql files and print the formatted tables directly to your terminal.
(sql_analysis.py and run_reports.py)

Generate Executive Charts
Run the visualization script to generate results for chosen metrics.
(metrics_analysis.py)
