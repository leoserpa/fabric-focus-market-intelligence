# How-to: Run and Test dbt Models in Microsoft Fabric

This operational guide provides actionable steps for compiling transformations, executing dimensional models, and validating data contract tests using **dbt (Data Build Tool)** integrated into **Microsoft Fabric**.

---

## Goal
Execute the **Gold** layer models and run automated assertion tests covering primary keys, nullability, and referential integrity.

---

## dbt Project Architecture

The dbt project resides in `fabric/05 - dbt/dbt_focus_intelligence.DataBuildToolJob/Code/dbt` and is organized as follows:

* **Sources (`models/gold/sources.yml`):** Points to the Lakehouse Silver Delta tables (`silver_focus_anuais`, `silver_focus_top5_anuais`, `silver_focus_inflacao_12m`, `silver_sgs_selic_meta`).
* **Dimensional Models (`models/gold/`):**
  * `dim_calendario.sql`: Daily calendar dimension spanning 2000 through 2035.
  * `dim_indicador.sql`: Metadata dimension holding economic indicator names and units.
  * `fct_expectativas_mercado.sql`: Fact table storing consensus expectations across annual horizons.
  * `fct_comparativo_top5.sql`: Fact table computing spreads between Top 5 institutions and the overall market.
  * `fct_juro_real_ex_ante.sql`: Fact table calculating daily ex-ante real rates via the Fisher Equation.

---

## Execution Workflow in Microsoft Fabric

### Method 1: Via the Fabric Web Interface (Recommended)
1. Within your Fabric workspace, locate the **dbt Job** item named **`dbt_focus_intelligence`**.
2. Click the item to open the dbt IDE inside Fabric.
3. In the top toolbar, standard quick buttons are available:
   * **Run:** Executes model compilation and materialization (`dbt run`).
   * **Test:** Executes data schema assertions (`dbt test`).
4. To run full end-to-end execution (compilation, materialization, and test verification in one pass):
   In the bottom console prompt, enter:
   ```bash
   dbt build
   ```
5. Monitor real-time logs in the output tab.

---

### Method 2: Running Targeted Models
When modifying specific logic:
* To execute only the real interest rate model:
  ```bash
  dbt run --select fct_juro_real_ex_ante
  ```
* To execute a model and all downstream dependencies:
  ```bash
  dbt run --select fct_comparativo_top5+
  ```

---

## Validating Data Quality Tests (dbt Test)

The project enforces assertions declared in `models/gold/schema.yml`:

| Model | Assertions Applied | Validation Objective |
| :--- | :--- | :--- |
| **dim_calendario** | `unique`, `not_null` on `data_sk` & `data` | Guarantees continuous, unique date surrogate keys. |
| **dim_indicador** | `unique`, `not_null` on `indicador_id` & `indicador` | Asserts uniqueness across the indicator catalog. |
| **fct_expectativas_mercado** | `not_null`, `relationships` to `dim_calendario` | Enforces referential integrity with the calendar dimension. |
| **fct_comparativo_top5** | `not_null`, `relationships` to `dim_calendario` | Prevents orphan records without corresponding dates. |
| **fct_juro_real_ex_ante** | `not_null`, `relationships` to `dim_calendario` | Validates that every Fisher calculation maps to valid time keys. |

To run all assertions:
```bash
dbt test
```

Expected passing output:
```text
Finished running 18 data tests ...
Completed successfully
Done. PASS=18 WARN=0 ERROR=0 SKIP=0 TOTAL=18
```

---

## Troubleshooting

### 1. Error: `Source 'lakehouse_silver.silver_...' does not exist`
* **Root cause:** Notebook `nb_02_bronze_to_silver` has not run yet or the Delta table was dropped.
* **Resolution:** Execute `nb_02_bronze_to_silver` before invoking dbt, or run the master pipeline `pl_focus_market_intelligence`.

### 2. T-SQL Casting and Floating-Point Issues
* **Root cause:** Fabric Warehouse uses T-SQL / SQL Server syntax. Integer division without casting truncates decimals.
* **Resolution:** Ensure date conversions use `CONVERT(VARCHAR(8), data, 112)` and division formulas use explicit floating points `(1.0 + (rate / 100.0))`.
