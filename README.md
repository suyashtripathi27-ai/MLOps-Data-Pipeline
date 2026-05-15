# MLOps-Data-Pipeline
Automated MLOps Pipeline: AI-Driven Data Routing & Processing
📌 Project Overview
A zero-cost, cloud-native MLOps pipeline built to completely automate the data preparation phase for Business Intelligence (BI) dashboards. The system leverages GitHub Actions for continuous integration and the Google Gemini LLM as an intelligent router to classify incoming data schemas, preventing pipeline failures and dynamically applying domain-specific data transformations.

🏗️ Pipeline Architecture & Flow
Data Ingestion (The Trigger): * Raw dataset files (.csv) are dropped into the data/raw/ directory.

This event automatically triggers a GitHub Actions CI/CD workflow, spinning up a virtual Ubuntu server.

The AI Router (Intelligent Classification): * A Python engine extracts the column headers of the new dataset and passes them to the Gemini 1.5 Flash API.

The AI acts as a "traffic cop," analyzing the schema to determine the industry domain (e.g., classifying a file with "Footfall" and "Sales" as RETAIL, and "osrm_time" and "route_type" as LOGISTICS).

Domain-Specific Processing (The Engine):

Logistics Logic: If logistics data is detected, the script automatically aggregates trip levels, cleans missing variables, and calculates efficiency KPIs like the delay_ratio.

Retail Logic: If retail data is detected, the script pivots to calculate daily conversion rates and total sales revenue.

Automated Delivery (Production):

The processed, BI-ready data is automatically committed and pushed back to the data/processed/ folder.

Power BI dashboards connected to this folder immediately reflect the clean, transformed data without any human intervention.

🛠️ Tech Stack
Automation: GitHub Actions (YAML)

Data Processing: Python (Pandas, OS, Sys)

Artificial Intelligence: Google Generative AI (Gemini API)

Presentation: Power BI

💡 Business Impact
Eliminates Manual ETL: Replaces hours of manual data cleaning and Excel manipulation with an instant, automated script.

Fault Tolerant: By using an LLM to inspect the data before processing, the pipeline safely routes or halts unknown data formats, preventing system crashes.

Scalable Architecture: New business units (like Finance or HR) can be added simply by updating the AI prompt and adding a new mathematical logic block to the Python script.
