# Azure Data Factory (ADF)

Azure Data Factory is Azure's cloud ETL service for data integration and transformation at scale.

## Key Concepts

| Concept | Description |
|---|---|
| **Pipeline** | Logical grouping of activities that perform a unit of work |
| **Activity** | A processing step in a pipeline (e.g., Copy, Notebook, Stored Procedure) |
| **Dataset** | A named view of data that references the data used in activities |
| **Linked Service** | Connection string / credentials to an external data source or compute |
| **Trigger** | Defines when a pipeline execution is kicked off (schedule, tumbling window, event) |
| **Integration Runtime** | Compute infrastructure used by ADF (Azure IR, Self-hosted IR, SSIS IR) |

## Common Patterns

### 1 – Copy Activity: Blob Storage → Azure SQL Database
The most fundamental ADF pattern — read files from ADLS/Blob and land them in a SQL sink.

### 2 – Incremental Load with Watermark
Track a `LastModified` or `RowVersion` column to copy only new/changed rows.

### 3 – Parameterized Pipelines
Use pipeline parameters and variables to build reusable, metadata-driven pipelines.

### 4 – Tumbling Window Trigger
Run a pipeline every hour/day and process data for exactly that window, with retry support.

## Files in this Module

| File | Description |
|---|---|
| `adf_pipeline_simulator.py` | Simulates an ADF Copy-Activity pipeline in pure Python |
| `sample_sales.csv` | Sample source data used by the simulator |

## Real-World Scenario

A retail company receives daily sales CSV files in Azure Blob Storage. An ADF pipeline:
1. Uses a **Schedule Trigger** (daily at 02:00 UTC)
2. Runs a **Copy Activity** to move the file into a staging table in Azure SQL DB
3. Calls a **Stored Procedure Activity** to merge staging data into the production table
4. Sends a **success/failure notification** via a Web Activity to a Teams webhook
