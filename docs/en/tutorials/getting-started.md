# Tutorial: Getting Started from Scratch

This tutorial guides you through the complete process of replicating the **Focus Market Intelligence** project in a new **Microsoft Fabric** workspace, from GitHub synchronization to the first pipeline run and report interaction in Power BI.

---

## Goal
By the end of this tutorial, you will have:
1. A Microsoft Fabric workspace connected to the GitHub repository.
2. All Bronze, Silver, and Gold layer tables created and populated.
3. The dbt dimensional models compiled and validated inside the Fabric Warehouse.
4. The 3-page Power BI report functioning in real time via Direct Lake mode.

**Estimated duration:** 25 to 35 minutes.

---

## Prerequisites
Before beginning, ensure you have:
* An active **Microsoft Fabric** account with access to a capacity (**Fabric Trial** or paid capacity **F2+**).
* Administrator or Contributor permissions in the target workspace.
* A **GitHub** account with read/write access to this repository.

---

## Step-by-Step Instructions

### Step 1: Create a Microsoft Fabric Workspace
1. Navigate to the official portal: [app.fabric.microsoft.com](https://app.fabric.microsoft.com).
2. On the left navigation pane, click **Workspaces** > **New workspace**.
3. Name your workspace (e.g., `WS_FOCUS_MARKET_INTELLIGENCE`).
4. Under **Advanced**, assign the workspace to your active **Fabric Capacity** (Trial or Dedicated).
5. Click **Apply**.

---

### Step 2: Connect the Workspace to Git (Source Control)
Microsoft Fabric supports bidirectional Git integration:
1. In the top navigation bar of your new workspace, click **Workspace settings**.
2. Select the **Git integration** tab.
3. Configure your connection parameters:
   * **Organization / Account:** Your GitHub organization or username.
   * **Repository:** The cloned or forked repository name.
   * **Branch:** `main`
   * **Git folder:** Enter `/fabric` *(note the leading slash; Fabric items reside in this subfolder)*.
4. Click **Connect and sync**.
5. Fabric will display the initial synchronization screen. Select the option to load artifacts from the remote branch into the workspace and confirm.

> **Result:** The following items will appear in the workspace:
> * `lk_focus_intelligence` (Lakehouse)
> * `nb_01_raw_to_bronze` and `nb_02_bronze_to_silver` (Notebooks)
> * `pl_focus_market_intelligence` (Data Pipeline)
> * `wh_focus_intelligence` (Warehouse)
> * `dbt_focus_intelligence` (dbt Job)
> * `sm_focus_market_intelligence` (Semantic Model)
> * `rpt_focus_market_intelligence` (Power BI Report)

---

### Step 3: Run the Ingestion and Processing Pipeline
To populate the tables and run end-to-end data transformations:
1. From the workspace item list, open the pipeline **`pl_focus_market_intelligence`**.
2. In the top toolbar, click **Run**.
3. The pipeline will execute the following activities sequentially:
   * **Activity 1:** Runs `nb_01_raw_to_bronze` (ingests data from BCB Olinda API and SGS 432 series into Bronze Delta tables).
   * **Activity 2:** Runs `nb_02_bronze_to_silver` (cleans, types, deduplicates, and standardizes into Silver Delta tables).
   * **Activity 3:** Triggers `dbt_focus_intelligence` (builds the Gold dimensional star schema inside the Warehouse).
4. Wait until all activities display a green **Succeeded** status.

---

### Step 4: Validate Data in the Warehouse
1. Return to the workspace root and open the Warehouse **`wh_focus_intelligence`**.
2. On the left object explorer, expand the **`gold`** schema.
3. Run quick diagnostic queries:
   ```sql
   SELECT TOP 10 * FROM gold.fct_juro_real_ex_ante ORDER BY data DESC;
   SELECT TOP 10 * FROM gold.fct_comparativo_top5 ORDER BY data DESC;
   SELECT TOP 10 * FROM gold.fct_expectativas_mercado ORDER BY data DESC;
   ```

---

### Step 5: Open and Inspect the Power BI Report
1. In the workspace, click the report **`rpt_focus_market_intelligence`**.
2. The report will load its 3 interactive executive pages:
   * **Page 1 (Panorama Focus):** IPCA, Selic, GDP, and Exchange Rate curves with last 30-day highlight.
   * **Page 2 (Market x Top 5):** Spread and divergence analysis (Hawkish vs. Dovish).
   * **Page 3 (Interest Rates & Inflation):** Continuous ex-ante real rate curve calculated via the Fisher Equation and Copom policy decisions.
3. Confirm that the top-right badge displays the latest observation date (e.g., `02/10/2026`).

---

## Conclusion
You have successfully deployed an enterprise-grade Analytics Engineering infrastructure on Microsoft Fabric.

**Recommended Next Steps:**
* To understand data models and quality assertions, read [How to Run and Test dbt Models](../how-to-guides/run-dbt-pipeline.md).
* For detailed theoretical and mathematical explanations, consult [Focus Methodology and Fisher Equation](../explanation/fisher-equation-methodology.md).
