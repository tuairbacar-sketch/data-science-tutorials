"""
fabric_lakehouse_demo.py
~~~~~~~~~~~~~~~~~~~~~~~~
Demonstrates Microsoft Fabric Lakehouse and Data Factory patterns using the
Fabric REST API and local simulation.

Patterns covered
----------------
1. List Fabric workspace items via REST API
2. Create a Lakehouse (REST API)
3. Upload a file to OneLake (Azure Data Lake Storage Gen2 endpoint)
4. Read a Delta table via the Lakehouse SQL Analytics Endpoint
5. Submit a Spark notebook job

Prerequisites
-------------
    pip install azure-identity requests pyodbc pandas

Environment variables
---------------------
    FABRIC_WORKSPACE_ID     GUID of the Fabric workspace
    FABRIC_CAPACITY_ID      GUID of the Fabric capacity (optional)
    AZURE_CLIENT_ID         Service Principal app ID
    AZURE_TENANT_ID         Azure AD tenant
    AZURE_CLIENT_SECRET     Service Principal secret

DRY_RUN is active when FABRIC_WORKSPACE_ID is not set.
"""

import json
import os
import time

DRY_RUN = not bool(os.getenv("FABRIC_WORKSPACE_ID"))

if DRY_RUN:
    print("[DRY RUN] Fabric credentials not set — printing operations only.\n")

WORKSPACE_ID = os.getenv("FABRIC_WORKSPACE_ID", "00000000-0000-0000-0000-000000000001")
FABRIC_API = "https://api.fabric.microsoft.com/v1"
ONELAKE_URL = "https://onelake.dfs.fabric.microsoft.com"


def _log(msg: str) -> None:
    print(f"  {msg}")


def get_token() -> str:
    if DRY_RUN:
        return "dry-run-token"
    from azure.identity import DefaultAzureCredential

    cred = DefaultAzureCredential()
    token = cred.get_token("https://api.fabric.microsoft.com/.default")
    return token.token


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


# ---------------------------------------------------------------------------
# 1. List workspace items
# ---------------------------------------------------------------------------

def list_workspace_items(token: str) -> None:
    print("[1] List Fabric workspace items")
    url = f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/items"
    _log(f"GET {url}")
    if not DRY_RUN:
        import requests

        resp = requests.get(url, headers=_headers(token))
        resp.raise_for_status()
        for item in resp.json().get("value", []):
            _log(f"  {item['type']:20s}  {item['displayName']}")
    else:
        _log("Response: [{type: 'Lakehouse', displayName: 'BronzeLakehouse'}, ...]")


# ---------------------------------------------------------------------------
# 2. Create a Lakehouse
# ---------------------------------------------------------------------------

def create_lakehouse(token: str, lakehouse_name: str = "SilverLakehouse") -> str:
    print(f"\n[2] Create Lakehouse: {lakehouse_name}")
    url = f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/lakehouses"
    body = {"displayName": lakehouse_name}
    _log(f"POST {url}")
    _log(f"Body: {json.dumps(body)}")
    if not DRY_RUN:
        import requests

        resp = requests.post(url, headers=_headers(token), json=body)
        resp.raise_for_status()
        lakehouse_id = resp.json()["id"]
        _log(f"Lakehouse created. ID: {lakehouse_id}")
        return lakehouse_id
    else:
        fake_id = "00000000-0000-0000-0000-000000000002"
        _log(f"Lakehouse created (dry run). ID: {fake_id}")
        return fake_id


# ---------------------------------------------------------------------------
# 3. Upload file to OneLake via ADLS Gen2 DFS endpoint
# ---------------------------------------------------------------------------

def upload_to_onelake(token: str, lakehouse_id: str, local_file: str, remote_path: str) -> None:
    print(f"\n[3] Upload file to OneLake")
    upload_url = f"{ONELAKE_URL}/{WORKSPACE_ID}/{lakehouse_id}/Files/{remote_path}"
    _log(f"PUT {upload_url}")
    if not DRY_RUN:
        import requests

        with open(local_file, "rb") as fh:
            data = fh.read()
        # OneLake uses ADLS Gen2 DFS REST — create file then append + flush
        create_resp = requests.put(
            upload_url + "?resource=file",
            headers={**_headers(token), "Content-Length": "0"},
        )
        create_resp.raise_for_status()
        append_resp = requests.patch(
            upload_url + "?action=append&position=0",
            headers={**_headers(token), "Content-Length": str(len(data))},
            data=data,
        )
        append_resp.raise_for_status()
        flush_resp = requests.patch(
            upload_url + f"?action=flush&position={len(data)}",
            headers=_headers(token),
        )
        flush_resp.raise_for_status()
        _log(f"Uploaded {len(data)} bytes → {remote_path}")
    else:
        _log(f"Upload '{local_file}' → OneLake path '{remote_path}'")


# ---------------------------------------------------------------------------
# 4. Query via SQL Analytics Endpoint
# ---------------------------------------------------------------------------

def query_sql_endpoint(lakehouse_id: str) -> None:
    print("\n[4] Query Lakehouse SQL Analytics Endpoint")
    server = f"{WORKSPACE_ID}.datawarehouse.fabric.microsoft.com"
    database = lakehouse_id
    sql = "SELECT TOP 5 * FROM dbo.orders ORDER BY order_date DESC"
    _log(f"Server: {server}")
    _log(f"SQL: {sql}")
    if not DRY_RUN:
        import pyodbc

        conn_str = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={server};DATABASE={database};"
            "Authentication=ActiveDirectoryServicePrincipal;"
            f"UID={os.getenv('AZURE_CLIENT_ID')};"
            f"PWD={os.getenv('AZURE_CLIENT_SECRET')};"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute(sql)
        for row in cursor.fetchall():
            _log(str(row))
        conn.close()
    else:
        _log("Result: [('ORD010', '2024-01-19', ...), ...]")


# ---------------------------------------------------------------------------
# 5. Submit Spark Notebook Job
# ---------------------------------------------------------------------------

def run_notebook(token: str, notebook_name: str = "SilverTransformation") -> None:
    print(f"\n[5] Submit Spark Notebook job: {notebook_name}")
    url = f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/items/{notebook_name}/jobs/instances?jobType=RunNotebook"
    body = {"executionData": {"parameters": {"input_path": "Files/raw/"}}}
    _log(f"POST {url}")
    _log(f"Body: {json.dumps(body)}")
    if not DRY_RUN:
        import requests

        resp = requests.post(url, headers=_headers(token), json=body)
        resp.raise_for_status()
        job_id = resp.headers.get("x-ms-operation-id", "unknown")
        _log(f"Notebook job submitted. Job ID: {job_id}")
        # Poll
        status_url = f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/items/{notebook_name}/jobs/instances/{job_id}"
        for _ in range(10):
            time.sleep(15)
            sr = requests.get(status_url, headers=_headers(token))
            status = sr.json().get("status")
            _log(f"  Status: {status}")
            if status in ("Completed", "Failed", "Cancelled"):
                break
    else:
        _log("Notebook job submitted (dry run). Poll every 15s for completion.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    token = get_token()
    list_workspace_items(token)
    lakehouse_id = create_lakehouse(token, "SilverLakehouse")

    from pathlib import Path

    sample = Path(__file__).parent.parent / "snowflake" / "sample_orders.csv"
    if sample.exists():
        upload_to_onelake(token, lakehouse_id, str(sample), "raw/sample_orders.csv")

    query_sql_endpoint(lakehouse_id)
    run_notebook(token, "SilverTransformation")
    print("\nDemo complete.")
