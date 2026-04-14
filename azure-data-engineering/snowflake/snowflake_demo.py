"""
snowflake_demo.py
~~~~~~~~~~~~~~~~~
Demonstrates Snowflake data engineering patterns using:
  - snowflake-connector-python  (standard SQL execution)
  - Snowpark Python              (DataFrame API inside Snowflake's engine)

Patterns covered
----------------
1. Connect to Snowflake
2. Create a database / schema / table
3. Load data via PUT (internal stage) + COPY INTO
4. Query with Python connector cursor
5. Snowpark DataFrame API
6. Stream + Task setup (CDC pattern)
7. Time Travel query
8. Zero-copy clone

Prerequisites
-------------
    pip install snowflake-connector-python snowflake-snowpark-python

Environment variables
---------------------
    SNOWFLAKE_ACCOUNT       e.g. xy12345.west-europe.azure
    SNOWFLAKE_USER
    SNOWFLAKE_PASSWORD
    SNOWFLAKE_WAREHOUSE     e.g. COMPUTE_WH
    SNOWFLAKE_DATABASE      e.g. AZURE_DE_DEMO
    SNOWFLAKE_SCHEMA        e.g. PUBLIC

DRY_RUN mode is active when SNOWFLAKE_ACCOUNT is not set.
"""

import os
from pathlib import Path

DRY_RUN = not bool(os.getenv("SNOWFLAKE_ACCOUNT"))

if DRY_RUN:
    print("[DRY RUN] Snowflake credentials not set — printing operations only.\n")

SAMPLE_CSV = Path(__file__).parent / "sample_orders.csv"

CONN_PARAMS = {
    "account":   os.getenv("SNOWFLAKE_ACCOUNT",   "xy12345.west-europe.azure"),
    "user":      os.getenv("SNOWFLAKE_USER",       "de_user"),
    "password":  os.getenv("SNOWFLAKE_PASSWORD",   "***"),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE",  "COMPUTE_WH"),
    "database":  os.getenv("SNOWFLAKE_DATABASE",   "AZURE_DE_DEMO"),
    "schema":    os.getenv("SNOWFLAKE_SCHEMA",     "PUBLIC"),
}


def _log(msg: str) -> None:
    print(f"  {msg}")


# ---------------------------------------------------------------------------
# 1-2. Connect and create objects
# ---------------------------------------------------------------------------

def setup_objects(cur) -> None:
    print("\n[1-2] Create database objects")
    ddl = [
        f"CREATE DATABASE IF NOT EXISTS {CONN_PARAMS['database']}",
        f"USE DATABASE {CONN_PARAMS['database']}",
        "CREATE SCHEMA IF NOT EXISTS PUBLIC",
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id    VARCHAR(20)   NOT NULL,
            order_date  DATE,
            customer_id VARCHAR(20),
            product     VARCHAR(100),
            quantity    INTEGER,
            unit_price  FLOAT,
            total       FLOAT,
            PRIMARY KEY (order_id)
        )
        """,
    ]
    for sql in ddl:
        _log(sql.strip().split("\n")[0])
        if not DRY_RUN:
            cur.execute(sql)


# ---------------------------------------------------------------------------
# 3. PUT + COPY INTO (internal stage)
# ---------------------------------------------------------------------------

def load_data(cur) -> None:
    print("\n[3] PUT local file to internal stage + COPY INTO")
    put_cmd = f"PUT file://{SAMPLE_CSV} @%orders AUTO_COMPRESS=TRUE"
    copy_cmd = """
        COPY INTO orders
        FROM @%orders
        FILE_FORMAT = (
            TYPE = CSV
            SKIP_HEADER = 1
            FIELD_OPTIONALLY_ENCLOSED_BY = '"'
            NULL_IF = ('')
        )
        ON_ERROR = 'CONTINUE'
    """
    for cmd in [put_cmd, copy_cmd]:
        _log(cmd.strip().split("\n")[0])
        if not DRY_RUN:
            cur.execute(cmd)
    if not DRY_RUN:
        rows = cur.fetchall()
        for r in rows:
            _log(str(r))


# ---------------------------------------------------------------------------
# 4. Query with Python connector
# ---------------------------------------------------------------------------

def query_with_connector(cur) -> None:
    print("\n[4] Query via Python connector cursor")
    sql = """
        SELECT product, COUNT(*) AS orders, ROUND(SUM(total), 2) AS revenue
        FROM orders
        GROUP BY product
        ORDER BY revenue DESC
    """
    _log(sql.strip().split("\n")[0])
    if not DRY_RUN:
        cur.execute(sql)
        import pandas as pd
        print(pd.DataFrame(cur.fetchall(), columns=[d[0] for d in cur.description]))
    else:
        _log("→ product | orders | revenue")


# ---------------------------------------------------------------------------
# 5. Snowpark DataFrame API
# ---------------------------------------------------------------------------

def demo_snowpark() -> None:
    print("\n[5] Snowpark Python DataFrame API")
    if DRY_RUN:
        _log("from snowflake.snowpark import Session")
        _log("session = Session.builder.configs(CONN_PARAMS).create()")
        _log("df = session.table('orders')")
        _log("df.group_by('product').agg(sum_('total').alias('revenue')).order_by(desc('revenue')).show()")
        return

    from snowflake.snowpark import Session
    from snowflake.snowpark.functions import sum_ as sp_sum, desc

    session = Session.builder.configs(CONN_PARAMS).create()
    df = session.table("orders")
    df.group_by("product").agg(sp_sum("total").alias("revenue")).order_by(desc("revenue")).show()
    session.close()


# ---------------------------------------------------------------------------
# 6. Stream + Task (CDC pattern — DDL only)
# ---------------------------------------------------------------------------

def demo_stream_task(cur) -> None:
    print("\n[6] Stream + Task (CDC pattern)")
    stream_sql = "CREATE STREAM IF NOT EXISTS orders_stream ON TABLE orders APPEND_ONLY = FALSE"
    task_sql = """
        CREATE TASK IF NOT EXISTS process_new_orders
            WAREHOUSE = COMPUTE_WH
            SCHEDULE = '60 MINUTE'
        AS
            INSERT INTO orders_summary
            SELECT product, SUM(total) AS revenue, CURRENT_TIMESTAMP AS updated_at
            FROM orders_stream
            WHERE METADATA$ACTION = 'INSERT'
            GROUP BY product
    """
    for sql in [stream_sql, task_sql]:
        _log(sql.strip().split("\n")[0])
        if not DRY_RUN:
            cur.execute(sql)


# ---------------------------------------------------------------------------
# 7. Time Travel
# ---------------------------------------------------------------------------

def demo_time_travel(cur) -> None:
    print("\n[7] Time Travel — query table as of 1 hour ago")
    sql = "SELECT * FROM orders AT (OFFSET => -3600) LIMIT 5"
    _log(sql)
    if not DRY_RUN:
        cur.execute(sql)
        for row in cur.fetchall():
            _log(str(row))


# ---------------------------------------------------------------------------
# 8. Zero-Copy Clone
# ---------------------------------------------------------------------------

def demo_zero_copy_clone(cur) -> None:
    print("\n[8] Zero-Copy Clone — instant dev/test environment")
    sql = "CREATE OR REPLACE TABLE orders_clone CLONE orders"
    _log(sql)
    if not DRY_RUN:
        cur.execute(sql)
        _log("Clone created instantly — no data copied, only metadata.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if DRY_RUN:
        cur = None
        setup_objects(cur)
        load_data(cur)
        query_with_connector(cur)
        demo_snowpark()
        demo_stream_task(cur)
        demo_time_travel(cur)
        demo_zero_copy_clone(cur)
    else:
        import snowflake.connector

        con = snowflake.connector.connect(**CONN_PARAMS)
        cur = con.cursor()
        try:
            setup_objects(cur)
            load_data(cur)
            query_with_connector(cur)
            demo_snowpark()
            demo_stream_task(cur)
            demo_time_travel(cur)
            demo_zero_copy_clone(cur)
        finally:
            cur.close()
            con.close()

    print("\nDemo complete.")
