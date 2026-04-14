# SQL & PySpark

SQL and PySpark are the two primary languages for data transformation in Azure Data Engineering pipelines. PySpark provides a programmatic DataFrame API while Spark SQL lets you write familiar ANSI SQL against the same engine.

## Key Concepts

| Concept | Description |
|---|---|
| **DataFrame API** | Lazily evaluated, immutable distributed dataset with a typed schema |
| **Catalyst Optimizer** | Spark's query optimizer — rewrites and optimises both DataFrame and SQL plans |
| **Broadcast Join** | Copies a small table to every worker to avoid a full shuffle |
| **Window Function** | Aggregation or ranking over a subset of rows without collapsing the result set |
| **Partition Pruning** | Skip irrelevant partitions based on filter predicates |
| **Bucketing** | Co-locate rows with the same key across files to speed up joins |

## DataFrame API vs Spark SQL

```python
# DataFrame API
result = (
    orders_df
    .filter(F.col("status") == "completed")
    .groupBy("region")
    .agg(F.sum("total").alias("revenue"))
    .orderBy(F.desc("revenue"))
)

# Equivalent Spark SQL
result = spark.sql("""
    SELECT region, SUM(total) AS revenue
    FROM orders
    WHERE status = 'completed'
    GROUP BY region
    ORDER BY revenue DESC
""")
```
Both produce identical query plans after Catalyst optimisation.

## Common Transformation Patterns

| Pattern | API |
|---|---|
| Filter rows | `df.filter()` / `WHERE` |
| Select columns | `df.select()` / `SELECT` |
| Add / derive column | `df.withColumn()` / derived column in `SELECT` |
| Aggregate | `df.groupBy().agg()` / `GROUP BY` |
| Join | `df.join(other, on, how)` / `JOIN` |
| Window function | `Window.partitionBy().orderBy()` / `OVER (PARTITION BY … ORDER BY …)` |
| Pivot | `df.groupBy().pivot().agg()` / `PIVOT` (Spark SQL extension) |
| Unpivot / Stack | `df.selectExpr("stack(…)")` / `UNPIVOT` |

## Files in this Module

| File | Description |
|---|---|
| `sql_pyspark_demo.ipynb` | Notebook covering joins, window functions, pivots, and performance tuning tips |

## Real-World Scenario

A logistics company needs a daily report showing:
- Total shipments per region per day (aggregation)
- Running 7-day average delivery time per carrier (window function)
- Late shipments joined with customer SLA table (join)
- Pivot: carriers as columns, regions as rows, shipment count as values

All transformations are authored in PySpark and the final result is saved as a Delta table for Power BI consumption.
