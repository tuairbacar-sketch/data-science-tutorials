# Azure Data Engineering Tutorials

A complete collection covering all high-demand Azure Data Engineering topics with practical code examples, notebooks, and real-world scenario questions.

## Modules

| # | Topic | Key Technologies | Directory |
|---|---|---|---|
| 1 | 🛠 Azure Data Factory (ADF) | Pipelines, Copy Activity, Triggers, Linked Services | [adf/](adf/) |
| 2 | ⚡ Azure Databricks | PySpark, Spark SQL, Delta Lake, Jobs | [databricks/](databricks/) |
| 3 | 🧠 Synapse Analytics | Dedicated SQL Pool, Serverless SQL, Spark Pools | [synapse-analytics/](synapse-analytics/) |
| 4 | 🗂 ADLS Gen2 | Hierarchical Namespace, ACLs, Medallion Architecture | [adls-gen2/](adls-gen2/) |
| 5 | 🧪 Delta Lake | ACID Transactions, Time Travel, MERGE, Schema Evolution | [delta-lake/](delta-lake/) |
| 6 | 🧾 SQL & PySpark | Joins, Window Functions, Pivot, Performance Tuning | [sql-pyspark/](sql-pyspark/) |
| 7 | 🐍 Python for Azure | Azure SDK, Blob Storage, Key Vault, ADF REST API | [python/](python/) |
| 8 | ❄️ Snowflake | Virtual Warehouses, Stages, COPY INTO, Snowpark | [snowflake/](snowflake/) |
| 9 | 🧱 Microsoft Fabric | Lakehouse, OneLake, Data Factory in Fabric, Shortcuts | [microsoft-fabric/](microsoft-fabric/) |
| 10 | 🔄 Scenario Questions | End-to-end pipeline design, interview Q&A | [scenario-questions/](scenario-questions/) |

## Getting Started

Each module is self-contained. Navigate to a module directory and follow its `README.md`.

Most Python scripts support a **dry-run mode** — they print the operations they would perform without needing real Azure credentials. Set the relevant environment variables (documented in each script's docstring) to run against a real Azure environment.

### Quick start (dry-run)

```bash
# Run the ADF pipeline simulator with sample data
cd adf/
python adf_pipeline_simulator.py

# Walk through scenario Q&A interactively
cd scenario-questions/
python scenario_pipeline_designer.py

# Print all scenario answers at once
python scenario_pipeline_designer.py --all
```

### Notebooks

Open `.ipynb` notebooks in:
- **Azure Databricks** (recommended for PySpark/Delta notebooks)
- **JupyterLab** / **VS Code** with `pip install pyspark delta-spark`

## Prerequisites by Module

| Module | Python packages |
|---|---|
| ADF simulator | stdlib only |
| Databricks | `pyspark`, `delta-spark` |
| Synapse Analytics | `duckdb`, `pandas` |
| ADLS Gen2 | `azure-storage-file-datalake`, `azure-identity` |
| Delta Lake | `pyspark`, `delta-spark` |
| SQL & PySpark | `pyspark` |
| Python / Azure SDK | `azure-storage-blob`, `azure-identity`, `azure-keyvault-secrets`, `azure-mgmt-datafactory` |
| Snowflake | `snowflake-connector-python`, `snowflake-snowpark-python` |
| Microsoft Fabric | `azure-identity`, `requests`, `pyodbc` |
| Scenario Questions | stdlib only |
