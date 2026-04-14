"""
adf_pipeline_simulator.py
~~~~~~~~~~~~~~~~~~~~~~~~~
Simulates a minimal Azure Data Factory Copy-Activity pipeline in pure Python.

Scenario
--------
Daily sales CSV files land in "Azure Blob Storage" (represented here as a
local directory).  The pipeline:
  1. Discovers new files since the last watermark timestamp.
  2. Reads each file (source dataset).
  3. Validates / transforms rows (equivalent to ADF Mapping Data Flows).
  4. Writes the cleaned rows to a "SQL sink" (represented as an in-memory
     list + CSV output).
  5. Updates the watermark so the next run only picks up newer files.

Run
---
    python adf_pipeline_simulator.py
"""

import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration  (would live in ADF Linked Services / Datasets in production)
# ---------------------------------------------------------------------------
SOURCE_DIR = Path(__file__).parent / "blob_source"      # simulated Blob container
SINK_FILE = Path(__file__).parent / "sql_sink_output.csv"
WATERMARK_FILE = Path(__file__).parent / "watermark.json"
PIPELINE_NAME = "CopySalesData_Pipeline"

SINK_COLUMNS = ["order_id", "order_date", "customer_id", "product", "quantity", "unit_price", "total"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_watermark() -> datetime:
    if WATERMARK_FILE.exists():
        data = json.loads(WATERMARK_FILE.read_text())
        return datetime.fromisoformat(data["last_run"])
    # Default: epoch — pick up every file on first run
    return datetime.fromtimestamp(0, tz=timezone.utc)


def save_watermark(ts: datetime) -> None:
    WATERMARK_FILE.write_text(json.dumps({"last_run": ts.isoformat()}))


def discover_new_files(since: datetime) -> list[Path]:
    """Return CSV files modified after *since*."""
    files = []
    for f in sorted(SOURCE_DIR.glob("*.csv")):
        mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
        if mtime > since:
            files.append(f)
    return files


def read_source(path: Path) -> list[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def transform_row(row: dict) -> dict | None:
    """
    Equivalent to an ADF Mapping Data Flow transformation:
      - Drop rows with missing order_id
      - Cast quantity / unit_price to numeric
      - Derive 'total' column
    """
    if not row.get("order_id"):
        return None
    try:
        quantity = float(row["quantity"])
        unit_price = float(row["unit_price"])
    except (ValueError, KeyError):
        return None
    return {
        "order_id": row["order_id"].strip(),
        "order_date": row.get("order_date", "").strip(),
        "customer_id": row.get("customer_id", "").strip(),
        "product": row.get("product", "").strip(),
        "quantity": int(quantity),
        "unit_price": round(unit_price, 2),
        "total": round(quantity * unit_price, 2),
    }


def write_sink(rows: list[dict]) -> None:
    mode = "a" if SINK_FILE.exists() else "w"
    with open(SINK_FILE, mode, newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=SINK_COLUMNS)
        if mode == "w":
            writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# Pipeline entry point
# ---------------------------------------------------------------------------

def run_pipeline() -> None:
    start_time = datetime.now(tz=timezone.utc)
    print(f"[{PIPELINE_NAME}] Starting at {start_time.isoformat()}")

    watermark = load_watermark()
    print(f"  Watermark (last run): {watermark.isoformat()}")

    new_files = discover_new_files(since=watermark)
    if not new_files:
        print("  No new files found. Pipeline finished with 0 rows copied.")
        return

    total_copied = 0
    total_skipped = 0

    for source_file in new_files:
        print(f"  Processing: {source_file.name}")
        raw_rows = read_source(source_file)
        transformed = [transform_row(r) for r in raw_rows]
        valid_rows = [r for r in transformed if r is not None]
        skipped = len(raw_rows) - len(valid_rows)
        write_sink(valid_rows)
        total_copied += len(valid_rows)
        total_skipped += skipped
        print(f"    Rows copied: {len(valid_rows)}  |  Rows skipped: {skipped}")

    save_watermark(start_time)

    print(
        f"[{PIPELINE_NAME}] Completed. "
        f"Total rows copied: {total_copied}  |  Total skipped: {total_skipped}"
    )
    print(f"  Output written to: {SINK_FILE}")


# ---------------------------------------------------------------------------
# Bootstrap sample source data if the blob_source directory is empty
# ---------------------------------------------------------------------------

def bootstrap_sample_data() -> None:
    SOURCE_DIR.mkdir(exist_ok=True)
    sample = SOURCE_DIR / "sales_2024_01_15.csv"
    if not sample.exists():
        import shutil
        src = Path(__file__).parent / "sample_sales.csv"
        if src.exists():
            shutil.copy(src, sample)


if __name__ == "__main__":
    bootstrap_sample_data()
    run_pipeline()
