# Azure Databricks

Azure Databricks is a fast, easy, and collaborative Apache Spark-based analytics platform optimized for Azure.

## Key Concepts

| Concept | Description |
|---|---|
| **Workspace** | Collaborative environment for notebooks, jobs, clusters, and data |
| **Cluster** | Set of computation resources (driver + worker nodes) running Spark |
| **Notebook** | Interactive document mixing code (Python/SQL/Scala/R), markdown, and visuals |
| **Job** | Scheduled or triggered execution of a notebook or JAR/Python script |
| **DBFS** | Databricks File System — abstraction over ADLS Gen2 / Blob Storage |
| **Unity Catalog** | Unified governance layer for data, AI models, and notebooks |
| **Delta Lake** | Default table format; provides ACID transactions on top of Parquet |

## Cluster Types

| Type | Use Case |
|---|---|
| All-purpose | Interactive notebooks, ad-hoc analysis |
| Job cluster | Automated pipelines; spun up/torn down per job run |
| SQL warehouse | BI queries via Databricks SQL |

## PySpark vs Spark SQL in Databricks

```python
# PySpark API
df = spark.read.format("delta").load("/mnt/sales/delta/orders")
df.filter(df.status == "completed").groupBy("region").agg({"revenue": "sum"}).show()

# Equivalent Spark SQL
spark.sql("""
    SELECT region, SUM(revenue) AS total_revenue
    FROM delta.`/mnt/sales/delta/orders`
    WHERE status = 'completed'
    GROUP BY region
""").show()
```

## Files in this Module

| File | Description |
|---|---|
| `databricks_pyspark_demo.ipynb` | Notebook covering cluster config, data ingestion, transformations, Delta write |

## Real-World Scenario

An e-commerce company runs nightly Databricks jobs to:
1. Read raw JSON clickstream data from ADLS Gen2
2. Parse and flatten nested fields with PySpark
3. Join with a customer dimension table in Delta Lake
4. Write the enriched dataset back as a Delta table
5. Trigger downstream Synapse Analytics refresh via REST API
