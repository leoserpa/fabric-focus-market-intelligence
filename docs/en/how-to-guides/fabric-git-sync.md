# How-to: Synchronize Microsoft Fabric with GitHub (Git Integration)

This guide explains how to utilize Microsoft Fabric's native **Git Integration (Source Control)** to version semantic models, reports, and pipelines directly within GitHub with full traceability and atomic change control.

---

## Goal
Manage workspace changes (Power BI, DAX, Pipelines, Notebooks), author atomic conventional commits, and maintain remote branch synchronization.

---

## How Git Works in Microsoft Fabric

Inside Microsoft Fabric:
* Artifacts are serialized into human-readable text formats:
  * **Reports:** `.pbip` format containing `visual.json`, `page.json`, and `report.json`.
  * **Semantic Models:** TMDL (`.tmdl`) files declaring tables, DAX measures, and relationships.
  * **Notebooks:** `.ipynb` notebooks or native code files.
  * **Pipelines:** JSON definitions of pipeline orchestration stages.
* Uncommitted changes trigger notifications in the **Source control** panel.

---

## Step-by-Step: Committing Changes from Fabric

### 1. Access the Source Control Panel
1. In the left workspace sidebar, click the branch icon labeled **Source control**.
2. The side drawer opens, showing the active branch (e.g., `main/fabric`) and modified item counts under the **Changes** tab.

### 2. Select Artifacts for Commit
You have granular control over what gets committed:
* For example, if you edited a DAX measure and a report chart:
  * Check `sm_focus_market_intelligence` (Semantic Model)
  * Check `rpt_focus_market_intelligence` (Report)
  * Leave unselected any unchanged or infrastructure items (such as `wh_focus_intelligence`).

### 3. Write a Professional Commit Message
Follow the **Conventional Commits** standard:
* `feat(report): finalize page 3 interest rates and inflation and update semantic model`
* `fix(dax): correct fisher equation division by zero handling`
* `refactor(dbt): optimize gold layer surrogate keys`

### 4. Confirm the Commit
1. Paste your message into the **Optional commit message** field.
2. Click **Commit**.
3. Fabric pushes serialized definitions directly to the remote GitHub branch.

---

## Pulling Remote Changes into Fabric (Sync / Update)

When changes are pushed to GitHub via terminal or pull request:
1. In the **Source control** pane, Fabric alerts you with notifications under the **Updates** tab.
2. Click **Update all**.
3. Fabric synchronizes workspace artifacts with the latest remote commit.

---

## Governance Best Practices
* **Atomic Commits:** Separate semantic model changes (`sm_...`) from visual changes (`rpt_...`) when publishing major updates.
* **Credential Hygiene:** Never store connection credentials in Git; leverage Azure Key Vault or Fabric managed service identities.
