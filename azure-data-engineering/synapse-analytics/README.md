# Azure Synapse Analytics

Azure Synapse Analytics is an enterprise analytics service that brings together data integration, enterprise data warehousing, and big data analytics.

## Key Concepts

| Concept | Description |
|---|---|
| **Dedicated SQL Pool** | Provisioned MPP data warehouse (formerly SQL DW); billed per DWU hour |
| **Serverless SQL Pool** | Query data in ADLS/Delta Lake on demand with T-SQL; billed per TB scanned |
| **Apache Spark Pool** | Managed Spark clusters inside Synapse for big data processing |
| **Synapse Pipelines** | ADF-compatible orchestration engine built into Synapse |
| **Synapse Link** | Near real-time analytical store for Cosmos DB / Dataverse without ETL |
| **Synapse Studio** | Unified IDE for SQL, Spark, pipelines, and data exploration |

## Dedicated vs. Serverless SQL Pool

| Feature | Dedicated SQL Pool | Serverless SQL Pool |
|---|---|---|
| Storage | Internal columnar storage | External (ADLS Gen2) |
| Scaling | Manual DWU scaling | Automatic |
| Best for | High-throughput BI workloads | Ad-hoc exploration, ELT |
| Pricing | Per DWU-hour (even when idle) | Per TB scanned |
| Table format | Native Synapse tables | Parquet, Delta, CSV, JSON |

## Integration with ADLS Gen2

```sql
-- Serverless SQL: query a Parquet file directly
SELECT TOP 100 *
FROM OPENROWSET(
    BULK 'https://myadls.dfs.core.windows.net/silver/orders/*.parquet',
    FORMAT = 'PARQUET'
) AS orders;

-- Create an external table over Delta Lake
CREATE EXTERNAL TABLE dbo.orders_delta
WITH (
    LOCATION = 'silver/orders/',
    DATA_SOURCE = my_adls_source,
    FILE_FORMAT = DeltaFormat
)
AS SELECT * FROM dbo.orders_staging;
```

## Files in this Module

| File | Description |
|---|---|
| `synapse_analytics_demo.py` | Simulates Synapse patterns: external tables, CETAS, incremental loads |
| `sample_events.json` | Sample JSON event data for serverless SQL demos |

## Real-World Scenario

A financial services firm uses Synapse Analytics to:
1. Land raw transaction data in ADLS Gen2 (Bronze layer)
2. Use **Synapse Spark** to clean and aggregate into a Silver layer
3. Create **external tables** in Serverless SQL Pool over the Silver Parquet files
4. Power **Power BI** reports directly from Serverless SQL without data movement
5. Run end-of-month summaries in the **Dedicated SQL Pool** for regulatory reporting
