"""
scenario_pipeline_designer.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Interactive CLI tool that walks through real-world Azure Data Engineering
scenario questions and model answers.

Usage
-----
    python scenario_pipeline_designer.py           # interactive mode
    python scenario_pipeline_designer.py --all     # print all Q&A pairs
"""

from __future__ import annotations

import argparse
import textwrap


# ---------------------------------------------------------------------------
# Scenario data
# ---------------------------------------------------------------------------

SCENARIOS: list[dict] = [
    {
        "id": 1,
        "title": "Retail – Daily Sales Ingestion Pipeline",
        "stack": "ADF · ADLS Gen2 · Databricks · Delta Lake · Power BI",
        "question": (
            "Design a pipeline that ingests daily CSV sales files from an "
            "on-premises SFTP server into a reporting-ready Delta table."
        ),
        "answer": textwrap.dedent("""\
            1. ADF Self-Hosted Integration Runtime reaches the on-premises SFTP server.
            2. Copy Activity moves files to adls://bronze/sales/YYYY/MM/DD/ (partitioned by date).
            3. An Event Trigger fires a Databricks job when a new file lands (storage event).
            4. Databricks job:
               - Reads raw CSV from Bronze
               - Drops nulls, deduplicates on order_id
               - Casts data types, derives 'total' column
               - Writes to Silver Delta table (MERGE to avoid duplicates)
            5. Gold Delta table aggregates daily revenue by store/region (scheduled job).
            6. Power BI DirectQuery connects via Synapse Serverless SQL Analytics Endpoint.

            Key design decisions:
            - Use MERGE (not overwrite) to make the pipeline idempotent.
            - Partition Delta tables by date for partition pruning in BI queries.
            - Store ADF linked-service credentials in Azure Key Vault.
        """),
    },
    {
        "id": 2,
        "title": "Finance – Incremental Load with Watermark",
        "stack": "ADF · Azure SQL DB · ADLS Gen2 · Synapse Analytics",
        "question": (
            "How would you implement an incremental load from an Azure SQL Database "
            "transactional system into a Synapse Dedicated SQL Pool?"
        ),
        "answer": textwrap.dedent("""\
            1. Add a LastModified DATETIME column (watermark) to the source table.
            2. ADF Lookup Activity reads the current watermark from a control table.
            3. Copy Activity uses a parameterised query:
               SELECT * FROM orders WHERE LastModified > '@{activity('Lookup').output.firstRow.Watermark}'
            4. Sink writes staged rows to a Synapse external/staging table.
            5. Stored Procedure Activity calls MERGE to upsert staging into the production table.
            6. Set Variable Activity saves the new watermark back to the control table.

            Key design decisions:
            - Use a control table for watermarks — never hard-code dates in pipelines.
            - Run MERGE inside a Synapse stored procedure to keep transformation logic in SQL.
            - Add a pipeline-level retry policy (3 retries, 30-minute interval).
        """),
    },
    {
        "id": 3,
        "title": "E-Commerce – Real-Time Event Processing",
        "stack": "Event Hubs · Stream Analytics · ADLS Gen2 · Delta Lake · Databricks",
        "question": (
            "Design a system to process real-time clickstream events and make them "
            "available for both real-time dashboards and batch ML model training."
        ),
        "answer": textwrap.dedent("""\
            1. Frontend sends events to Azure Event Hubs (Kafka-compatible, 32 partitions).
            2. Azure Stream Analytics job:
               - 1-minute tumbling window aggregates → Cosmos DB (real-time dashboard)
               - Raw events → ADLS Gen2 in Parquet format (batch path)
            3. Databricks Structured Streaming reads Event Hubs:
               spark.readStream.format('eventhubs').load()
               Writes to Bronze Delta table with trigger(processingTime='1 minute').
            4. Delta Live Tables pipeline: Bronze → Silver → Gold.
            5. Gold Delta table = ML feature store for scheduled model training jobs.

            Key design decisions:
            - Two consumers on Event Hubs: Stream Analytics (real-time) + Databricks (near-real-time).
            - Use Delta's MERGE for deduplication in the Silver layer.
            - Set Event Hubs retention to 7 days for replayability.
        """),
    },
    {
        "id": 4,
        "title": "Healthcare – Secure Data Lake for PHI",
        "stack": "ADLS Gen2 · Azure Purview · Unity Catalog · Key Vault · Private Endpoints",
        "question": (
            "How would you design a secure, compliant data lake for "
            "PHI (Protected Health Information)?"
        ),
        "answer": textwrap.dedent("""\
            1. Dedicated ADLS Gen2 account with private endpoints — no public internet access.
            2. POSIX ACLs + Azure RBAC enforcing principle of least privilege per team.
            3. Customer-Managed Keys (CMK) in Azure Key Vault for encryption at rest.
            4. All pipeline access via Managed Identity — zero stored credentials.
            5. Azure Purview for data cataloguing, sensitivity labels, and lineage.
            6. Databricks Unity Catalog: column-level masking on PII/PHI columns.
            7. Diagnostic logs + Azure Monitor alerts for anomalous access patterns.
            8. HIPAA-aligned audit logging with 7-year retention in Azure Storage (WORM).

            Key design decisions:
            - Network isolation (private endpoints + VNet) before any data lands.
            - Classify ALL columns at ingestion with Purview — not retroactively.
            - Test access controls with a dedicated 'audit' service principal quarterly.
        """),
    },
    {
        "id": 5,
        "title": "SaaS – Multi-Tenant Data Platform",
        "stack": "Microsoft Fabric · Snowflake · ADF · Python",
        "question": (
            "How would you architect a multi-tenant analytics platform where each "
            "customer has isolated data but shares the same compute?"
        ),
        "answer": textwrap.dedent("""\
            1. Each tenant gets a dedicated Fabric Lakehouse in a shared workspace (logical isolation).
            2. OneLake Shortcuts expose cross-tenant reference data (e.g. product catalogue) without duplication.
            3. ADF parameterised pipelines use tenant_id as a pipeline parameter:
               - Single pipeline definition, many runs (one per tenant).
               - Python orchestrator triggers runs in parallel via ADF REST API.
            4. Row-level security in the Fabric Semantic Model restricts data per authenticated user.
            5. Snowflake Virtual Warehouses scale independently per tenant SLA tier:
               - Gold tier: dedicated XL warehouse (always-on)
               - Silver tier: shared L warehouse (auto-suspend 5 min)
               - Bronze tier: shared XS warehouse (auto-suspend 1 min)
            6. Tenant config stored in Azure SQL DB (tenant_id, adls_path, warehouse_name, sla_tier).

            Key design decisions:
            - Logical isolation (separate Lakehouses) is simpler than physical (separate accounts).
            - Never mix tenant data in the same Delta table — partition key ≠ isolation.
            - Automate tenant onboarding: Python script provisions Lakehouse + Snowflake warehouse.
        """),
    },
]


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def _divider(char: str = "─", width: int = 60) -> str:
    return char * width


def print_scenario(s: dict, show_answer: bool = True) -> None:
    print(f"\n{_divider('═')}")
    print(f"  Scenario {s['id']}: {s['title']}")
    print(f"  Stack: {s['stack']}")
    print(_divider())
    print(f"\n  Q: {s['question']}\n")
    if show_answer:
        print("  A:")
        for line in s["answer"].splitlines():
            print(f"     {line}")
    print()


# ---------------------------------------------------------------------------
# Interactive mode
# ---------------------------------------------------------------------------

def interactive_mode() -> None:
    print(_divider("═"))
    print("  Azure Data Engineering – Scenario Q&A")
    print(_divider("═"))
    print("\nAvailable scenarios:")
    for s in SCENARIOS:
        print(f"  [{s['id']}] {s['title']}")

    while True:
        choice = input("\nEnter scenario number (or 'q' to quit): ").strip()
        if choice.lower() == "q":
            break
        try:
            n = int(choice)
            s = next((x for x in SCENARIOS if x["id"] == n), None)
            if s:
                print_scenario(s, show_answer=False)
                input("  Press ENTER to reveal the answer...")
                print_scenario(s, show_answer=True)
            else:
                print(f"  No scenario with ID {n}.")
        except ValueError:
            print("  Please enter a valid number.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Azure Data Engineering Scenario Q&A")
    parser.add_argument("--all", action="store_true", help="Print all scenarios and answers")
    args = parser.parse_args()

    if args.all:
        for s in SCENARIOS:
            print_scenario(s, show_answer=True)
    else:
        interactive_mode()
