# Delta Lake

Delta Lake is an open-source storage layer that brings ACID transactions, scalable metadata handling, and unified streaming/batch data processing to data lakes.

## Key Concepts

| Concept | Description |
|---|---|
| **ACID Transactions** | Atomicity, Consistency, Isolation, Durability — guaranteed even on object storage |
| **Transaction Log** | `_delta_log/` directory containing JSON commit files that record every change |
| **Schema Enforcement** | Writes that violate the table schema are rejected automatically |
| **Schema Evolution** | Add new columns without rewriting the table using `mergeSchema` |
| **Time Travel** | Query any historical version of a table with `VERSION AS OF` or `TIMESTAMP AS OF` |
| **MERGE (Upsert)** | Efficiently insert-update-delete in one atomic operation |
| **Optimize & Z-Order** | Compact small files and co-locate related data for faster queries |
| **Change Data Feed** | Track row-level inserts/updates/deletes for downstream consumers |

## Delta Lake Table Lifecycle

```
Bronze (raw)  →  Silver (cleaned)  →  Gold (aggregated)
     ↑ append-only       ↑ MERGE / update        ↑ overwrite / aggregate
```

## Common Operations

```python
from delta.tables import DeltaTable

# Time Travel
spark.read.format("delta").option("versionAsOf", 3).load("/delta/orders").show()

# MERGE (upsert)
DeltaTable.forPath(spark, "/delta/orders").alias("t").merge(
    updates.alias("s"), "t.order_id = s.order_id"
).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()

# Schema evolution
df.write.format("delta").option("mergeSchema", "true").mode("append").save("/delta/orders")

# Vacuum old files (retain 7 days by default)
DeltaTable.forPath(spark, "/delta/orders").vacuum()
```

## Files in this Module

| File | Description |
|---|---|
| `delta_lake_demo.ipynb` | Notebook covering CRUD, time travel, MERGE, schema evolution, optimize |

## Real-World Scenario

A streaming pipeline writes raw IoT sensor readings every minute to a Bronze Delta table. A scheduled Databricks job:
1. **MERGEs** new readings into a Silver Delta table (deduplication)
2. **Z-ORDERs** by `device_id` and `timestamp` for query performance
3. Exposes a Gold Delta table with hourly aggregates for dashboards
4. Uses **Change Data Feed** to push incremental changes to downstream ML feature store
