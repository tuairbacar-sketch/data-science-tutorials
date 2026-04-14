# Microsoft Fabric

Microsoft Fabric is an all-in-one analytics platform that unifies data engineering, data science, real-time analytics, and business intelligence under a single SaaS product built on top of OneLake.

## Key Concepts

| Concept | Description |
|---|---|
| **OneLake** | Single, tenant-wide data lake — all Fabric items store data here automatically |
| **Lakehouse** | Combines a data lake (ADLS Gen2 / Delta) with a SQL analytics endpoint |
| **Warehouse** | Fully transactional T-SQL data warehouse (dedicated compute) |
| **Data Factory in Fabric** | ADF-compatible pipelines natively integrated in Fabric |
| **Notebook** | PySpark / SQL / R notebooks backed by Spark clusters |
| **Eventhouse** | Real-time analytics store powered by Azure Data Explorer (KQL) |
| **Semantic Model** | Power BI dataset built directly on Lakehouse / Warehouse tables |
| **Shortcut** | Virtual reference to data in ADLS Gen2, S3, or other Lakehouses — no copy |

## Medallion Architecture in Fabric

```
OneLake
├── Bronze Lakehouse   ← raw ingest via Data Factory or Eventstream
├── Silver Lakehouse   ← cleaned Delta tables via PySpark Notebooks
└── Gold Lakehouse     ← aggregated Delta tables + SQL Endpoint for Power BI
```

## Data Factory in Fabric vs. Azure Data Factory

| Feature | ADF | Fabric Data Factory |
|---|---|---|
| Deployment | Standalone Azure resource | Part of Fabric workspace |
| Storage | Any Azure / external | OneLake-first |
| Triggers | Schedule, Event, Tumbling Window | Same + Fabric item triggers |
| Billing | Pay-as-you-go (DIUs) | Fabric capacity (F-SKU) |
| Git integration | Azure DevOps / GitHub | GitHub / Azure DevOps |

## Files in this Module

| File | Description |
|---|---|
| `fabric_lakehouse_demo.py` | Demonstrates Lakehouse creation, Shortcut, and notebook patterns |

## Real-World Scenario

A retail organisation migrates its analytics platform to Microsoft Fabric:
1. **Data Factory in Fabric** ingests POS data from on-premises SQL Server into Bronze Lakehouse
2. A **PySpark Notebook** cleans and conforms data to Silver Delta tables
3. A **Shortcut** exposes historical ADLS Gen2 data without copying
4. The **SQL Analytics Endpoint** on the Gold Lakehouse powers **Power BI** reports
5. **Activator** (Fabric real-time intelligence) triggers alerts when inventory drops below threshold
