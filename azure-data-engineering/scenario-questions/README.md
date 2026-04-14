# Real Company-Based Scenario Questions

This module contains interview-style scenario questions and answers covering end-to-end Azure Data Engineering pipeline design.

## Scenarios

### Scenario 1 — Retail: Daily Sales Ingestion Pipeline
**Company type:** Large multi-national retailer  
**Stack:** ADF · ADLS Gen2 · Databricks · Delta Lake · Power BI

> **Q:** Design a pipeline that ingests daily CSV sales files from an on-premises SFTP server into a reporting-ready Delta table.

**Answer outline:**
1. Use ADF **Self-Hosted Integration Runtime** to reach the on-premises SFTP
2. **Copy Activity** moves files to `adls://bronze/sales/YYYY/MM/DD/`
3. An **Event Trigger** fires a Databricks job when a new file lands
4. Databricks job cleans, deduplicates, and writes to `silver/sales` as a Delta table
5. A Gold Delta table aggregates daily revenue by store/region
6. Power BI DirectQuery connects to the Gold table via Synapse Serverless SQL endpoint

---

### Scenario 2 — Finance: Incremental Load with CDC
**Company type:** Investment bank  
**Stack:** ADF · Azure SQL DB · ADLS Gen2 · Synapse Analytics

> **Q:** How would you implement an incremental load from an Azure SQL Database transactional system into a Synapse Dedicated SQL Pool?

**Answer outline:**
1. Add a `LastModified DATETIME` column (watermark) to the source table
2. ADF **Lookup Activity** reads the current watermark from a control table
3. **Copy Activity** uses a parameterised query: `WHERE LastModified > @watermark`
4. Sink writes staged rows to a Synapse staging table
5. **Stored Procedure Activity** calls `MERGE` to upsert staging into the production table
6. **Set Variable Activity** saves the new watermark back to the control table

---

### Scenario 3 — E-Commerce: Real-Time Event Processing
**Company type:** Online marketplace  
**Stack:** Azure Event Hubs · Azure Stream Analytics · ADLS Gen2 · Delta Lake

> **Q:** Design a system to process real-time clickstream events and make them available for both real-time dashboards and batch ML model training.

**Answer outline:**
1. Frontend sends events to **Azure Event Hubs** (Kafka-compatible)
2. **Azure Stream Analytics** job:
   - Tumbling window (1-minute) aggregates land in **Azure Cosmos DB** (real-time dashboard)
   - Raw events land in **ADLS Gen2** in Parquet format (batch path)
3. Databricks **Structured Streaming** reads the Event Hubs source and writes to a **Bronze Delta table**
4. A **Delta Live Tables** pipeline runs bronze → silver → gold transformations
5. The Gold Delta table is the feature store for ML model training

---

### Scenario 4 — Healthcare: Data Lake Governance
**Company type:** Hospital network  
**Stack:** ADLS Gen2 · Azure Purview · Unity Catalog · Key Vault · Private Endpoints

> **Q:** How would you design a secure, compliant data lake for PHI (Protected Health Information)?

**Answer outline:**
1. Store PHI in a dedicated ADLS Gen2 account with **private endpoints** (no public internet access)
2. Use **POSIX ACLs** + **Azure RBAC** — principle of least privilege per team
3. Encrypt data at rest with **Customer-Managed Keys** (CMK) in Azure Key Vault
4. All ADF / Databricks access uses **Managed Identity** — no stored credentials
5. Enable **Azure Purview** for data cataloguing and lineage tracking
6. Implement **column-level masking** in Synapse / Databricks Unity Catalog for PII columns
7. Enable **diagnostic logs** + **Azure Monitor** alerts for suspicious access patterns

---

### Scenario 5 — SaaS: Multi-Tenant Data Platform
**Company type:** B2B SaaS analytics provider  
**Stack:** Microsoft Fabric · Snowflake · ADF · Python

> **Q:** How would you architect a multi-tenant analytics platform where each customer has isolated data but shares the same compute?

**Answer outline:**
1. Each tenant gets a dedicated **Fabric Lakehouse** inside a shared workspace (logical isolation)
2. **OneLake Shortcuts** expose cross-tenant reference data without duplication
3. ADF parameterised pipelines use tenant ID as a pipeline parameter — single pipeline, many tenants
4. **Row-level security** in the Fabric Semantic Model restricts data per authenticated user
5. Snowflake **Virtual Warehouses** scale independently per tenant SLA tier
6. Python orchestrator reads a tenant config JSON and triggers per-tenant ADF runs in parallel

---

## Files in this Module

| File | Description |
|---|---|
| `scenario_pipeline_designer.py` | Interactive CLI tool to walk through pipeline design decisions |
