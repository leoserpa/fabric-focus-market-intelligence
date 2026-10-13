# Technical Documentation - Focus Market Intelligence

Welcome to the official technical documentation for **Focus Market Intelligence**, an end-to-end Analytics Engineering project built on **Microsoft Fabric**, **dbt**, and **Power BI**, dedicated to monitoring and modeling macroeconomic expectations published by the Central Bank of Brazil (BCB).

This documentation adheres strictly to the **[Diataxis](https://diataxis.fr/)** technical authoring framework, organizing technical knowledge into four distinct quadrants:

---

## The Four Diataxis Quadrants

```
                     PRACTICAL (Action)
                           ▲
                           │
       TUTORIALS           │        HOW-TO GUIDES
    Learning-oriented      │       Problem-oriented
     (First steps)         │      (Specific recipes)
                           │
STUDY ─────────────────────┼───────────────────── WORK
(For newcomers)            │                      (Day-to-day)
                           │
      EXPLANATION          │          REFERENCE
 Understanding-oriented    │     Information-oriented
(Architecture & Theory)    │     (Tables, DAX & APIs)
                           │
                           ▼
                   THEORETICAL (Knowledge)
```

---

### 1. [Tutorials](./tutorials/getting-started.md)
Learning-oriented. Step-by-step practical guides designed to take a newcomer from cloning the repository to a working deployment.
* **[Getting Started](./tutorials/getting-started.md)**: Prerequisites, Microsoft Fabric capacity provisioning, artifact import, and first pipeline run.

---

### 2. [How-to Guides](./how-to-guides/run-dbt-pipeline.md)
Problem-oriented. Actionable recipes for daily operational tasks.
* **[How to Run and Test dbt Models](./how-to-guides/run-dbt-pipeline.md)**: Steps to compile transformations, execute `dbt run`, and validate data contracts with `dbt test`.
* **[How to Synchronize Fabric with GitHub](./how-to-guides/fabric-git-sync.md)**: Microsoft Fabric source control configuration, branches, and atomic commit practices.

---

### 3. [Reference](./reference/data-dictionary.md)
Information-oriented. Authoritative technical descriptions, schemas, and specifications.
* **[Data Dictionary and Schemas](./reference/data-dictionary.md)**: Table definitions across Lakehouse (Bronze/Silver), Warehouse (Gold), and relationship keys.
* **[DAX Measures Catalog](./reference/dax-measures.md)**: Formal catalog of all DAX measures in the semantic model (`sm_focus_market_intelligence`), including the Fisher Equation, Top 5 spreads, and dynamic format strings.

---

### 4. [Explanation](./explanation/architecture.md)
Understanding-oriented. Deep-dive discussions on design decisions and financial theory.
* **[Data Architecture in Microsoft Fabric](./explanation/architecture.md)**: Rationale behind Medallion Architecture, dbt inside Fabric Warehouse, and Direct Lake storage mode.
* **[Focus Survey Methodology and Fisher Equation](./explanation/fisher-equation-methodology.md)**: How the Central Bank collects expectations (Base 0 vs. Base 1) and mathematical derivation of the ex-ante real interest rate.

---

## Repository Structure

```text
focus-market-intelligence/
├── README.md                      # Portuguese repository showcase
├── README.en.md                   # English repository showcase
├── docs/                          # Technical documentation (Diataxis)
│   ├── assets/screenshots/        # High-resolution report panel screenshots
│   ├── README.md                  # Language selector hub
│   ├── pt-br/                     # Portuguese documentation suite
│   └── en/                        # English documentation suite
└── fabric/                        # Synchronized Microsoft Fabric artifacts
    ├── 01 - Lakehouse/            # lk_focus_intelligence (Delta Lake)
    ├── 02 - Notebooks/            # PySpark: Ingestion & Curation
    ├── 03 - Pipelines/            # pl_focus_market_intelligence (Data Pipeline)
    ├── 04 - Warehouse/            # wh_focus_intelligence (Gold Warehouse)
    ├── 05 - dbt/                  # dbt_focus_intelligence (Dimensional models)
    ├── 06 - Semantic Models/      # sm_focus_market_intelligence (TMDL / Direct Lake)
    └── 07 - Reports/              # rpt_focus_market_intelligence (Power BI PBIP)
```
