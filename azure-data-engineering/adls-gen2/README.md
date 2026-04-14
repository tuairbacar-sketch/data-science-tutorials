# Azure Data Lake Storage Gen2 (ADLS Gen2)

ADLS Gen2 combines the scalability of Azure Blob Storage with a hierarchical namespace, fine-grained access control, and POSIX-compliant ACLs — making it the standard storage layer for Azure big data workloads.

## Key Concepts

| Concept | Description |
|---|---|
| **Hierarchical Namespace (HNS)** | Enables true directory semantics and atomic rename/move operations |
| **Container** | Top-level grouping of data (analogous to a Blob container or S3 bucket) |
| **Directory** | Logical folder in the HNS; rename/delete is O(1) unlike Blob Storage |
| **POSIX ACLs** | Fine-grained access at file/directory level (read, write, execute) |
| **Managed Identity** | Preferred authentication method for Azure services (no keys required) |
| **Lifecycle Policy** | Automatically tier or delete blobs based on age/last access |

## Medallion Architecture on ADLS Gen2

```
adls-account/
├── bronze/        ← raw ingest (immutable, append-only)
│   ├── sales/
│   └── clickstream/
├── silver/        ← cleaned & conformed
│   ├── orders/
│   └── customers/
└── gold/          ← aggregated, BI-ready
    └── kpi_summary/
```

## Authentication Options

| Method | When to use |
|---|---|
| Managed Identity | ADF, Databricks, Synapse running inside Azure |
| Service Principal | CI/CD pipelines, external applications |
| Storage Account Key | Development / testing only — never in production |
| SAS Token | Temporary delegated access, short-lived |

## Files in this Module

| File | Description |
|---|---|
| `adls_gen2_demo.py` | Demonstrates ADLS Gen2 operations via the `azure-storage-file-datalake` SDK |
| `sample_customers.csv` | Sample data uploaded and queried in the demo |

## Integration with ADF and Databricks

- **ADF**: Use ADLS Gen2 Linked Service with Managed Identity; mount as a source/sink dataset
- **Databricks**: Mount ADLS Gen2 with `dbutils.fs.mount()` or use `abfss://` paths directly with a Service Principal or Managed Identity
- **Synapse**: Use `OPENROWSET` or create external data sources pointing to the `dfs.core.windows.net` endpoint
