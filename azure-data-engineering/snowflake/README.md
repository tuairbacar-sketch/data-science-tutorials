# Snowflake on Azure

Snowflake is a cloud-native data platform that runs natively on Azure. It is commonly used alongside ADLS Gen2 and Azure Data Factory in Azure Data Engineering architectures.

## Key Concepts

| Concept | Description |
|---|---|
| **Virtual Warehouse** | Independent compute cluster; scales without affecting storage or other warehouses |
| **Database / Schema / Table** | Standard three-level namespace for organising data objects |
| **Stage** | Named location (internal or external) for staging files before COPY INTO |
| **External Stage** | Points to ADLS Gen2 / Azure Blob — files stay in Azure, Snowflake reads them |
| **COPY INTO** | High-throughput bulk load from a stage into a table |
| **Snowpark** | Python / Java / Scala DataFrame API that runs compute inside Snowflake |
| **Streams & Tasks** | CDC mechanism + scheduled SQL execution (Snowflake's native orchestration) |
| **Time Travel** | Query historical data up to 90 days back |
| **Zero-Copy Cloning** | Instant, space-efficient copy of tables / schemas / databases |

## Loading Data from ADLS Gen2

```sql
-- 1. Create an external stage pointing to ADLS Gen2
CREATE OR REPLACE STAGE my_adls_stage
  URL = 'azure://myaccount.blob.core.windows.net/silver/orders/'
  CREDENTIALS = (AZURE_SAS_TOKEN = '<token>');

-- 2. List files in the stage
LIST @my_adls_stage;

-- 3. Load data with COPY INTO
COPY INTO orders
FROM @my_adls_stage/orders_2024_01_15.csv
FILE_FORMAT = (TYPE = CSV SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"');
```

## Files in this Module

| File | Description |
|---|---|
| `snowflake_demo.py` | Demonstrates Snowflake connector + Snowpark patterns for loading and querying data |
| `sample_orders.csv` | Sample data used in the COPY INTO demo |

## Real-World Scenario

A SaaS analytics company:
1. Lands raw subscription events in **ADLS Gen2** (Bronze)
2. An **ADF pipeline** triggers a Snowflake **COPY INTO** to load events into a staging table
3. A Snowflake **Task** runs every hour to merge staging data into the production fact table
4. A **Snowflake Stream** captures CDC changes and feeds a real-time dashboard
5. **Snowpark Python** notebooks run ML feature engineering inside Snowflake's compute
