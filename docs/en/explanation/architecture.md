# Explanation: Data Architecture in Microsoft Fabric

This document discusses architectural and conceptual design decisions behind the **Focus Market Intelligence** platform, explaining technical motivations for selecting **Microsoft Fabric**, **dbt**, and **Direct Lake** storage mode.

---

## The Microsoft Fabric and OneLake Paradigm

Traditionally, building an end-to-end analytical pipeline involving government API ingestion, heavy data processing, dimensional modeling, and interactive BI required stitching together multiple cloud services:
* Azure Data Factory (orchestration)
* Azure Databricks or Synapse Spark (distributed processing)
* Azure SQL or Snowflake (data warehousing)
* Power BI Service (semantic models & visualization)

**Microsoft Fabric** consolidates these capabilities into a single SaaS platform unified by **OneLake** (the unified analytical data lake). Every compute engine natively reads and writes open-format **Delta Lake (Parquet with transaction logs)**, eliminating data silos and redundant copies.

---

## Medallion Architecture (Bronze -> Silver -> Gold)

We implement the standard Medallion Architecture to ensure data governance, progressive quality elevation, and complete auditability:

```mermaid
flowchart LR
    subgraph Bronze ["1. Bronze Layer (Raw)"]
        direction TB
        B1["PySpark Notebook<br/>nb_01_raw_to_bronze"]
        B2[("Lakehouse Delta Lake<br/>lk_focus_intelligence")]
        B1 --> B2
    end

    subgraph Silver ["2. Silver Layer (Curated)"]
        direction TB
        S1["PySpark Notebook<br/>nb_02_bronze_to_silver"]
        S2[("Lakehouse Delta Lake<br/>silver_*")]
        S1 --> S2
    end

    subgraph Gold ["3. Gold Layer (Dimensional)"]
        direction TB
        G1["dbt Core Job<br/>T-SQL / dbt build"]
        G2[("Fabric Warehouse<br/>wh_focus_intelligence")]
        G1 --> G2
    end

    B2 --> S1
    S2 --> G1
```

### 1. Bronze Layer (Raw)
* **Goal:** Capture raw payloads from Central Bank APIs (Olinda OData and SGS series) exactly as emitted by source endpoints, preserving full history.
* **Tool:** PySpark Notebooks (`nb_01_raw_to_bronze`).
* **Rationale:** In the event of schema shifts or regulatory re-audit, raw source files remain preserved in Delta Lake for zero-loss recomputation.

### 2. Silver Layer (Curated and Standardized)
* **Goal:** Perform type coercion, timestamp parsing, null handling, deduplication, and indicator normalization.
* **Tool:** PySpark Notebooks (`nb_02_bronze_to_silver`).
* **Rationale:** Apache Spark scales memory processing across historical series, enforcing formal schemas and temporal validations.

### 3. Gold Layer (Dimensional Star Schema)
* **Goal:** Deliver normalized facts and dimensions optimized for analytical queries.
* **Tool:** Fabric Data Warehouse orchestrated by **dbt** (`dbt_focus_intelligence`).
* **Rationale:** Enables standard SQL modeling, surrogate key generation (`data_sk`), clean joins, and referential integrity assertions.

![Star Schema Semantic Model](../../assets/screenshots/04-modelo-semantico-star-schema.png)

---

## Why dbt (Data Build Tool) Inside Fabric Warehouse?

Gold layer transformations are maintained in **dbt** for four essential reasons:
1. **Analytics Code as Software:** All models are declarative, version-controlled SQL files tracked in Git.
2. **Automated DAG Lineage:** dbt infers execution ordering automatically through `ref()` and `source()` macros.
3. **Automated Assertion Testing:** Models enforce schema tests (`schema.yml`) validating uniqueness, non-nullability, and referential constraints prior to report consumption.
4. **Idempotent Deployments:** Table materialization guarantees deterministic, atomic builds on each run.

---

## Direct Lake: Overcoming the Import vs. DirectQuery Dilemma

The semantic model `sm_focus_market_intelligence` accesses Gold Warehouse tables via **Direct Lake**:

* **Traditional Import Mode:** Incurs data duplication, memory footprint constraints, and scheduled refresh latency.
* **Traditional DirectQuery:** Translates visual interactions into live SQL queries, resulting in query latency and database load.
* **Fabric Direct Lake:** Reads columnar Parquet files directly from OneLake storage at in-memory speeds **without duplicating data into memory caches**, ensuring instant freshness upon pipeline completion.

---

## Operational Lineage in Microsoft Fabric (Lineage View)

Below is the actual operational lineage graph of the artifacts within the Microsoft Fabric workspace:

![Operational Workspace Lineage in Microsoft Fabric](../../assets/screenshots/05-linhagem-workspace-fabric.png)

### Understanding the Lineage Topology and Direct Lake

Reviewing the Fabric lineage view highlights two essential architectural characteristics:
1. **Pipeline Orchestration:** The `pl_focus_market_intelligence` pipeline orchestrates the sequential execution of ingestion (`nb_01_raw_to_bronze`), curation (`nb_02_bronze_to_silver`), and dimensional modeling (`dbt_focus_intelligence`).
2. **dbt T-SQL Materialization:** dbt connects to the Data Warehouse (`wh_focus_intelligence`) via standard T-SQL database connections to materialize Gold tables. The Fabric visual lineage tracker does not introspect external dynamic SQL executions as declarative UI dependencies.
3. **Direct Lake Consumption:** The semantic model `sm_focus_market_intelligence` reads Delta tables from the Warehouse natively in Direct Lake mode. Consequently, no legacy dataset refresh task is needed at the pipeline's end, ensuring immediate analytical availability.
