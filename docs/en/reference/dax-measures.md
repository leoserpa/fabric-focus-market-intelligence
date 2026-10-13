# Reference: DAX Measures Catalog

This document formally specifies all DAX measures defined in table `_Medidas` within the semantic model **`sm_focus_market_intelligence`**, explaining their computational logic, business purpose, and formatting rules.

---

## 1. Header and Refresh Status Measures

### `Última Data da Observação`
Computes the most recent available date across the 3 fact tables, ensuring dynamic updates regardless of differing source update times.
```dax
Última Data da Observação = 
VAR DataFocus = CALCULATE(MAX(fct_expectativas_mercado[data]), REMOVEFILTERS())
VAR DataTop5  = CALCULATE(MAX(fct_comparativo_top5[data]), REMOVEFILTERS())
VAR DataJuros = CALCULATE(MAX(fct_juro_real_ex_ante[data]), REMOVEFILTERS())
RETURN MAX(DataFocus, MAX(DataTop5, DataJuros))
```

### `HTML Observação Mais Recente`
Generates HTML markup for the *HTML Content* custom visual badge, styling descriptive text in `#626E73` and the latest date in bold dark `#23282B`.
```dax
HTML Observação Mais Recente = 
VAR DataObs = [Última Data da Observação]
VAR TextoData = IF(ISBLANK(DataObs), "Sem dados", FORMAT(DataObs, "dd/MM/yyyy"))
RETURN
    "<div style='width:100%;height:100%;min-height:56px;box-sizing:border-box;display:flex;align-items:center;" &
        "gap:12px;padding:0 18px;border:1px solid #CBD2D5;border-radius:7px;background:#FFFFFF;" &
        "font-family:Segoe UI,Arial,sans-serif;font-size:15px;color:#626E73;white-space:nowrap;'>" &
        "<span>Observação mais recente</span>" &
        "<strong style='font-size:15px;font-weight:700;color:#23282B;'>" & TextoData & "</strong>" &
    "</div>"
```

---

## 2. Page 1 Measures (Panorama Focus)

### `KPI IPCA 2026`, `KPI Selic 2026`, `KPI PIB 2026`, `KPI Câmbio 2026`
Calculates the latest broad market median forecast for each core indicator for the year 2026.
* Formats: `0.00%` for rates/percentages; `R$ #,0.00` for currency.

### `Data Início Destaque`
Calculates the cutoff date defining the **last 30 days** window based on the latest observation date:
```dax
Data Início Destaque = 
VAR DatasComValor =
    FILTER(
        ALLSELECTED(dim_calendario[data]),
        NOT ISBLANK(CALCULATE([Mediana Mercado]))
    )
VAR UltimaData = MAXX(DatasComValor, dim_calendario[data])
VAR DataCorte = UltimaData - 30
RETURN
    COALESCE(
        MAXX(FILTER(DatasComValor, dim_calendario[data] <= DataCorte), dim_calendario[data]),
        MINX(DatasComValor, dim_calendario[data])
    )
```

### `Mediana Histórico` and `Mediana Recente`
Powers the continuous two-color line visual:
* **`Mediana Histórico`:** Returns values when `data <= [Data Início Destaque]` (grey `#A4AAAD` line).
* **`Mediana Recente`:** Returns values when `data >= [Data Início Destaque]` (orange `#FA590B` line).

### `Último Valor do Gráfico`
Isolates the final data point on the line chart, rendering an accent marker and clean callout label without visual clutter.

---

## 3. Page 2 Measures (Market x Top 5)

### `Delta IPCA 2026` and `Delta Selic 2026`
Quantifies divergence between Top 5 institutions and the broad market:
$$\Delta = \text{Top 5 Median} - \text{Market Median}$$
* Formatted with delta symbols as `+0.00 p.p.` or `-0.22 p.p.`.

### `Cor Spread IPCA`
Conditional formatting metric for divergence column charts:
* `Divergence > 0` (Top 5 more Hawkish than market): Accent orange `#FA590B`.
* `Divergence <= 0` (Top 5 neutral or Dovish): Muted grey `#626E73`.

---

## 4. Page 3 Measures (Interest Rates & Inflation)

### `KPI Juro Real Ex-Ante`
Computes the latest ex-ante real rate via the Fisher Equation on the most recent observation date:
```dax
KPI Juro Real Ex-Ante = 
VAR DataMax = CALCULATE(MAX(fct_juro_real_ex_ante[data]), REMOVEFILTERS(dim_calendario))
RETURN
CALCULATE(
    AVERAGE(fct_juro_real_ex_ante[taxa_juro_real_ex_ante]),
    fct_juro_real_ex_ante[data] = DataMax
)
```
* Formatting: `0.00%` (e.g., `8.69%`).

### `KPI Selic Vigente`
Effective Copom target Selic rate from series SGS 432.
* Formatting: `0.00%` (e.g., `13.75%`).

### `KPI Inflação 12M`
Smoothed 12-month rolling IPCA forecast median (Base 1 - 5 business days).
* Formatting: `0.00%` (e.g., `4.65%`).

### Line Pointers (`Ponteiro Juro Real`, `Ponteiro Selic Vigente`, `Ponteiro Inflação 12M`)
Filters values strictly on the final available business day across the 6-month historical trajectory, rendering the orange accent dot and callout data label over neutral grey series lines.
