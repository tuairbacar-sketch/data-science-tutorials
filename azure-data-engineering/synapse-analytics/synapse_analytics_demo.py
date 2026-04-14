"""
synapse_analytics_demo.py
~~~~~~~~~~~~~~~~~~~~~~~~~
Simulates key Azure Synapse Analytics patterns using Python + DuckDB
(a local analytical engine that mirrors Synapse Serverless SQL semantics).

Patterns demonstrated
---------------------
1. Serverless SQL: query Parquet / JSON files with OPENROWSET-style SELECT
2. Create External Table As Select (CETAS) — materialise a query result
3. Incremental load with watermark (mirrors Synapse Dedicated Pool pattern)
4. Partition elimination (common Synapse Serverless optimisation)

Run
---
    pip install duckdb pandas
    python synapse_analytics_demo.py
"""

import json
import os
import tempfile
from pathlib import Path

import duckdb
import pandas as pd

DATA_DIR = Path(__file__).parent
EVENTS_FILE = DATA_DIR / "sample_events.json"
TEMP_DIR = Path(tempfile.mkdtemp(prefix="synapse_demo_"))

# ---------------------------------------------------------------------------
# 0. Bootstrap — create a DuckDB in-memory connection
# ---------------------------------------------------------------------------
con = duckdb.connect()
print("=" * 60)
print("Azure Synapse Analytics Demo (local simulation via DuckDB)")
print("=" * 60)

# ---------------------------------------------------------------------------
# 1. Serverless SQL — query JSON directly (OPENROWSET equivalent)
# ---------------------------------------------------------------------------
print("\n[1] Serverless SQL: query JSON events file")

events_df = pd.read_json(EVENTS_FILE)
# Register as a DuckDB view (equivalent to OPENROWSET in Synapse)
con.register("events_view", events_df)

result = con.execute("""
    SELECT
        event_type,
        COUNT(*)            AS event_count,
        COUNT(DISTINCT user_id) AS unique_users,
        ROUND(AVG(duration_seconds), 2) AS avg_duration
    FROM events_view
    GROUP BY event_type
    ORDER BY event_count DESC
""").df()
print(result.to_string(index=False))

# ---------------------------------------------------------------------------
# 2. CETAS — materialise aggregated result to Parquet
# ---------------------------------------------------------------------------
print("\n[2] CETAS: materialise aggregated events to Parquet")

agg_parquet = TEMP_DIR / "agg_events.parquet"
con.execute(f"""
    COPY (
        SELECT
            event_type,
            DATE_TRUNC('day', CAST(event_time AS TIMESTAMP)) AS event_day,
            COUNT(*) AS events,
            ROUND(AVG(duration_seconds), 2) AS avg_duration
        FROM events_view
        GROUP BY event_type, DATE_TRUNC('day', CAST(event_time AS TIMESTAMP))
    ) TO '{agg_parquet}' (FORMAT PARQUET)
""")
print(f"  Written to: {agg_parquet}")

# Read back (simulates querying the external table)
readback = con.execute(f"SELECT * FROM read_parquet('{agg_parquet}') ORDER BY event_day, event_type").df()
print(readback.to_string(index=False))

# ---------------------------------------------------------------------------
# 3. Incremental Load with Watermark (Dedicated SQL Pool pattern)
# ---------------------------------------------------------------------------
print("\n[3] Incremental load — only process events newer than watermark")

watermark = pd.Timestamp("2024-01-15 10:00:00")
incremental = con.execute(f"""
    SELECT *
    FROM events_view
    WHERE CAST(event_time AS TIMESTAMP) > TIMESTAMP '{watermark}'
    ORDER BY event_time
""").df()
print(f"  Watermark: {watermark}  |  New rows: {len(incremental)}")
print(incremental[["event_id", "event_type", "event_time", "user_id"]].to_string(index=False))

# ---------------------------------------------------------------------------
# 4. Partition Elimination (Synapse Serverless optimisation)
# ---------------------------------------------------------------------------
print("\n[4] Partition elimination — filter on partitioned column")

# Write sample data partitioned by event_type
for etype, grp in events_df.groupby("event_type"):
    part_path = TEMP_DIR / f"event_type={etype}" / "data.parquet"
    part_path.parent.mkdir(parents=True, exist_ok=True)
    grp.to_parquet(part_path, index=False)

# Query only the 'click' partition
click_path = TEMP_DIR / "event_type=click" / "data.parquet"
if click_path.exists():
    clicks = con.execute(f"SELECT * FROM read_parquet('{click_path}')").df()
    print(f"  Rows in 'click' partition: {len(clicks)}")
    print(clicks[["event_id", "user_id", "duration_seconds"]].to_string(index=False))

print("\nDemo complete.")
