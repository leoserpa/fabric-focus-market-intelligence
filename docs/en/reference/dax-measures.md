# Reference: Complete DAX Measures Catalog

This document formally specifies all **40 DAX measures** implemented in table `_Medidas` within the semantic model **`sm_focus_market_intelligence`** ([_Medidas.tmdl](../../../fabric/06%20-%20Semantic%20Models/sm_focus_market_intelligence.SemanticModel/definition/tables/_Medidas.tmdl)), providing verbatim formulas, business purpose, visual role, and formatting rules.

---

## Executive Summary of Measures

| Category | Measure Count | Primary Purpose |
| :--- | :---: | :--- |
| **1. Header & Dynamic Metadata** | 2 | Top report refresh badge using native Unicode bold numerals and max date calculation. |
| **2. Base Projection Metrics** | 5 | Foundational aggregations for market consensus, Top 5, spreads, Selic rate, and Fisher. |
| **3. Page 1: Focus Overview (Lines & Highlights)** | 6 | Continuous dual-color trend lines (last 30-day window in orange) and isolated endpoint callouts. |
| **4. Page 1: Executive KPIs (Reference Year 2026)** | 5 | Single-value cards for IPCA, Selic, GDP Total, and USD/BRL Exchange Rate. |
| **5. Page 2: Market vs. Top 5 (Divergence Analysis)** | 13 | Institutional Hawkish/Dovish spreads, conditional HEX colors, and chart markers. |
| **6. Page 3: Interest Rates & Inflation (Fisher & Policy)** | 9 | Continuous real rate curves, official daily Copom Selic target, and end-of-series pointers. |
| **Total** | **40** | **All production measures in the Direct Lake semantic model.** |

---

## 1. Header & Dynamic Metadata

### 1.1 `Texto Observação Mais Recente`
* **Purpose:** Dynamically constructs the top badge string across all report pages, determining the most recent observation date among the 3 fact tables. Converts date numbers into native bold Unicode characters (`𝟬` to `𝟵`) for crisp typography without requiring custom HTML visual components.
* **DAX Formula:**
```dax
Texto Observação Mais Recente = 
VAR DataJur = CALCULATE(MAX(fct_juro_real_ex_ante[data]), ALL())
VAR DataTop = CALCULATE(MAX(fct_comparativo_top5[data]), ALL())
VAR DataExp = CALCULATE(MAX(fct_expectativas_mercado[data]), ALL())
VAR DataFinal = COALESCE(DataJur, DataTop, DataExp)

VAR Dia = FORMAT(DAY(DataFinal), "00")
VAR Mes = FORMAT(MONTH(DataFinal), "00")
VAR Ano = FORMAT(YEAR(DataFinal), "0000")
VAR DataTexto = Dia & "/" & Mes & "/" & Ano

-- Converts each digit into native Unicode bold representation
VAR DataNegrito = 
    SUBSTITUTE(
    SUBSTITUTE(
    SUBSTITUTE(
    SUBSTITUTE(
    SUBSTITUTE(
    SUBSTITUTE(
    SUBSTITUTE(
    SUBSTITUTE(
    SUBSTITUTE(
    SUBSTITUTE(DataTexto, 
        "0", "𝟬"), 
        "1", "𝟭"), 
        "2", "𝟮"), 
        "3", "𝟯"), 
        "4", "𝟰"), 
        "5", "𝟱"), 
        "6", "𝟲"), 
        "7", "𝟳"), 
        "8", "𝟴"), 
        "9", "𝟵")

RETURN
"Data da observação mais recente: " & DataNegrito
```

### 1.2 `Última Data Focus`
* **Purpose:** Returns the maximum date available in `fct_expectativas_mercado`, bypassing calendar filter context.
* **DAX Formula:**
```dax
Última Data Focus = 
CALCULATE(
    MAX(fct_expectativas_mercado[data]),
    REMOVEFILTERS(dim_calendario[data])
)
```

---

## 2. Base Projection Metrics

### 2.1 `Mediana Mercado`
* **Purpose:** Computes the overall market median forecast in `fct_expectativas_mercado` within the active filter context.
* **DAX Formula:**
```dax
Mediana Mercado = 
AVERAGE(fct_expectativas_mercado[mediana])
```

### 2.2 `Mediana Top 5`
* **Purpose:** Computes the medium-term Top 5 forecast median in `fct_comparativo_top5`.
* **DAX Formula:**
```dax
Mediana Top 5 = 
AVERAGE(fct_comparativo_top5[mediana_top5])
```

### 2.3 `Divergência Top 5`
* **Purpose:** Direct spread between Top 5 institutions and the overall market ($\text{Top 5} - \text{Market}$).
* **DAX Formula:**
```dax
Divergência Top 5 = 
[Mediana Top 5] - [Mediana Mercado]
```

### 2.4 `Juro Real Ex-Ante`
* **Purpose:** Retrieves the daily ex-ante real interest rate calculated via the Fisher Equation in the Warehouse.
* **DAX Formula:**
```dax
Juro Real Ex-Ante = 
SELECTEDVALUE(fct_juro_real_ex_ante[taxa_juro_real_ex_ante])
```

### 2.5 `Selic Atual`
* **Purpose:** Retrieves the effective annual Selic target rate from the real interest rate fact table.
* **DAX Formula:**
```dax
Selic Atual = 
SELECTEDVALUE(fct_juro_real_ex_ante[taxa_selic_meta_aa])
```

---

## 3. Page 1: Focus Overview (Lines & 30-Day Window)

### 3.1 `Data Início Destaque`
* **Purpose:** Finds the latest valid date on the line chart and subtracts 30 days to define the recent accent window.
* **DAX Formula:**
```dax
Data Início Destaque = 
VAR DatasComValor =
    FILTER(
        ALLSELECTED(dim_calendario[data]),
        NOT ISBLANK(CALCULATE([Mediana Mercado]))
    )
VAR UltimaData =
    MAXX(DatasComValor, dim_calendario[data])
VAR DataCorte = UltimaData - 30
RETURN
    COALESCE(
        MAXX(
            FILTER(
                DatasComValor,
                dim_calendario[data] <= DataCorte
            ),
            dim_calendario[data]
        ),
        MINX(DatasComValor, dim_calendario[data])
    )
```

### 3.2 `Mediana Histórico`
* **Purpose:** Feeds the muted grey (`#A4AAAD`) historical line segment for dates prior to or on the 30-day cutoff date.
* **DAX Formula:**
```dax
Mediana Histórico = 
VAR DataAtual = SELECTEDVALUE(dim_calendario[data])
VAR DataInicio = [Data Início Destaque]
RETURN
    IF(
        NOT ISBLANK(DataInicio)
            && DataAtual <= DataInicio,
        [Mediana Mercado],
        BLANK()
    )
```

### 3.3 `Mediana Recente`
* **Purpose:** Feeds the accent orange (`#FA590B`) line segment for dates inside the recent 30-day window.
* **DAX Formula:**
```dax
Mediana Recente = 
VAR DataAtual = SELECTEDVALUE(dim_calendario[data])
VAR DataInicio = [Data Início Destaque]
RETURN
    IF(
        NOT ISBLANK(DataInicio)
            && DataAtual >= DataInicio,
        [Mediana Mercado],
        BLANK()
    )
```

### 3.4 `Último Valor do Gráfico`
* **Purpose:** Returns the numeric value exclusively at the final series date, rendering a marker dot without visual noise.
* **DAX Formula:**
```dax
Último Valor do Gráfico = 
VAR UltimaData =
    MAXX(
        FILTER(
            ALLSELECTED(dim_calendario[data]),
            NOT ISBLANK(CALCULATE([Mediana Mercado]))
        ),
        dim_calendario[data]
    )
RETURN
    IF(
        SELECTEDVALUE(dim_calendario[data]) = UltimaData,
        [Mediana Mercado],
        BLANK()
    )
```

### 3.5 `Último Valor Percentual`
* **Purpose:** String formatted as percentage (`0.00%`) strictly on the line's final point (IPCA, Selic, GDP).
* **DAX Formula:**
```dax
Último Valor Percentual = 
VAR UltimaData =
    MAXX(
        FILTER(
            ALLSELECTED(dim_calendario[data]),
            NOT ISBLANK(CALCULATE([Mediana Mercado]))
        ),
        dim_calendario[data]
    )
RETURN
    IF(
        SELECTEDVALUE(dim_calendario[data]) = UltimaData,
        FORMAT([Mediana Mercado], "0.00", "pt-BR") & "%",
        BLANK()
    )
```

### 3.6 `Último Valor Câmbio`
* **Purpose:** String formatted as BRL currency (`R$ 0.00`) strictly on the final point of the USD/BRL currency line.
* **DAX Formula:**
```dax
Último Valor Câmbio = 
VAR UltimaData =
    MAXX(
        FILTER(
            ALLSELECTED(dim_calendario[data]),
            NOT ISBLANK(CALCULATE([Mediana Mercado]))
        ),
        dim_calendario[data]
    )
RETURN
    IF(
        SELECTEDVALUE(dim_calendario[data]) = UltimaData,
        "R$ " & FORMAT([Mediana Mercado], "0.00", "pt-BR"),
        BLANK()
    )
```

---

## 4. Page 1: Executive KPIs (Reference Year 2026)

### 4.1 `KPI Última Mediana`
* **Purpose:** Core measure for executive cards; evaluates market median on the latest date while disregarding calendar filters.
* **DAX Formula:**
```dax
KPI Última Mediana = 
VAR DataMaisRecente =
    CALCULATE(
        MAX(fct_expectativas_mercado[data]),
        REMOVEFILTERS(dim_calendario),
        fct_expectativas_mercado[mediana] <> BLANK()
    )
RETURN
    IF(
        ISBLANK(DataMaisRecente),
        BLANK(),
        CALCULATE(
            [Mediana Mercado],
            REMOVEFILTERS(dim_calendario),
            fct_expectativas_mercado[data] = DataMaisRecente
        )
    )
```

### 4.2 `KPI IPCA 2026`
* **Purpose:** Latest IPCA forecast for reference year 2026 under Base 0 calculation.
* **DAX Formula:**
```dax
KPI IPCA 2026 = 
CALCULATE(
    [KPI Última Mediana],
    fct_expectativas_mercado[indicador] = "IPCA",
    fct_expectativas_mercado[ano_referencia] = 2026,
    fct_expectativas_mercado[base_calculo] = 0
)
```

### 4.3 `KPI Selic 2026`
* **Purpose:** Latest Selic forecast for reference year 2026 under Base 0 calculation.
* **DAX Formula:**
```dax
KPI Selic 2026 = 
CALCULATE(
    [KPI Última Mediana],
    fct_expectativas_mercado[indicador] = "Selic",
    fct_expectativas_mercado[ano_referencia] = 2026,
    fct_expectativas_mercado[base_calculo] = 0
)
```

### 4.4 `KPI PIB 2026`
* **Purpose:** Latest GDP Total growth forecast for reference year 2026 under Base 0 calculation.
* **DAX Formula:**
```dax
KPI PIB 2026 = 
CALCULATE(
    [KPI Última Mediana],
    fct_expectativas_mercado[indicador] = "PIB Total",
    fct_expectativas_mercado[ano_referencia] = 2026,
    fct_expectativas_mercado[base_calculo] = 0
)
```

### 4.5 `KPI Dólar 2026`
* **Purpose:** Latest Exchange Rate (USD/BRL) forecast for reference year 2026 under Base 0 calculation.
* **DAX Formula:**
```dax
KPI Dólar 2026 = 
CALCULATE(
    [KPI Última Mediana],
    fct_expectativas_mercado[indicador] = "Câmbio",
    fct_expectativas_mercado[ano_referencia] = 2026,
    fct_expectativas_mercado[base_calculo] = 0
)
```

---

## 5. Page 2: Market vs. Top 5 (Divergence Analysis)

### 5.1 `Mediana Mercado Comparativo`
* **Purpose:** Market consensus median within comparative table `fct_comparativo_top5`.
* **DAX Formula:**
```dax
Mediana Mercado Comparativo = 
AVERAGE(fct_comparativo_top5[mediana_mercado])
```

### 5.2 `Divergência Top 5 Spread`
* **Purpose:** Mean institutional spread in percentage points between Top 5 and broad market.
* **DAX Formula:**
```dax
Divergência Top 5 Spread = 
AVERAGE(fct_comparativo_top5[divergencia_top5_mercado])
```

### 5.3 `Cor da Divergência`
* **Purpose:** Conditional HEX color for columns: Orange (`#E66C37`) for Hawkish ($\ge 0$) and Dark grey (`#A4AAAD`) for Dovish ($< 0$).
* **DAX Formula:**
```dax
Cor da Divergência = 
IF(
    [Divergência Top 5 Spread] >= 0,
    "#E66C37",  -- Orange (Top 5 higher / Hawkish)
    "#A4AAAD"   -- Dark grey (Top 5 lower / Dovish)
)
```

### 5.4 `KPI Divergência IPCA`
* **Purpose:** Point-in-time spread for IPCA 2026 on the latest available date.
* **DAX Formula:**
```dax
KPI Divergência IPCA = 
VAR DataRecente = 
    CALCULATE(
        MAX(fct_comparativo_top5[data]),
        REMOVEFILTERS(dim_calendario),
        fct_comparativo_top5[indicador] = "IPCA",
        fct_comparativo_top5[ano_referencia] = 2026
    )
VAR Diferenca = 
    CALCULATE(
        AVERAGE(fct_comparativo_top5[divergencia_top5_mercado]),
        REMOVEFILTERS(dim_calendario),
        fct_comparativo_top5[indicador] = "IPCA",
        fct_comparativo_top5[ano_referencia] = 2026,
        fct_comparativo_top5[data] = DataRecente
    )
RETURN
    Diferenca
```

### 5.5 `KPI Divergência Selic`
* **Purpose:** Point-in-time spread for Selic 2026 on the latest available date.
* **DAX Formula:**
```dax
KPI Divergência Selic = 
VAR DataRecente = 
    CALCULATE(
        MAX(fct_comparativo_top5[data]),
        REMOVEFILTERS(dim_calendario),
        fct_comparativo_top5[indicador] = "Selic",
        fct_comparativo_top5[ano_referencia] = 2026
    )
VAR Diferenca = 
    CALCULATE(
        AVERAGE(fct_comparativo_top5[divergencia_top5_mercado]),
        REMOVEFILTERS(dim_calendario),
        fct_comparativo_top5[indicador] = "Selic",
        fct_comparativo_top5[ano_referencia] = 2026,
        fct_comparativo_top5[data] = DataRecente
    )
RETURN
    Diferenca
```

### 5.6 `Mercado Última Data`
* **Purpose:** Market median evaluated on the global latest date of the comparative fact table.
* **DAX Formula:**
```dax
Mercado Última Data = 
VAR UltimaData = CALCULATE(MAX(fct_comparativo_top5[data]), REMOVEFILTERS())
RETURN
CALCULATE(
    AVERAGE(fct_comparativo_top5[mediana_mercado]),
    fct_comparativo_top5[data] = UltimaData
)
```

### 5.7 `Top 5 Última Data`
* **Purpose:** Top 5 median evaluated on the global latest date of the comparative fact table.
* **DAX Formula:**
```dax
Top 5 Última Data = 
VAR UltimaData = CALCULATE(MAX(fct_comparativo_top5[data]), REMOVEFILTERS())
RETURN
CALCULATE(
    AVERAGE(fct_comparativo_top5[mediana_top5]),
    fct_comparativo_top5[data] = UltimaData
)
```

### 5.8 `Divergência Última Data`
* **Purpose:** Spread on the latest date to supply comparative matrices and tables.
* **DAX Formula:**
```dax
Divergência Última Data = 
VAR UltimaData = CALCULATE(MAX(fct_comparativo_top5[data]), REMOVEFILTERS())
RETURN
CALCULATE(
    AVERAGE(fct_comparativo_top5[divergencia_top5_mercado]),
    fct_comparativo_top5[data] = UltimaData
)
```

### 5.9 `Cor da Diferença Tabela`
* **Purpose:** Table matrix formatting rule: Orange (`#E66C37`) for positive spread, Graphite (`#23282B`) for negative, and Neutral grey (`#8C969A`) for zero.
* **DAX Formula:**
```dax
Cor da Diferença Tabela = 
VAR Dif = [Divergência Última Data]
RETURN
SWITCH(
    TRUE(),
    Dif > 0, "#E66C37",   -- Focus Institutional Orange
    Dif < 0, "#23282B",   -- Dark Graphite
    "#8C969A"             -- Neutral Grey (Consensus)
)
```

### 5.10 `Último Rótulo Top 5`
* **Purpose:** Formatted string percentage (`0.00%`) on the Top 5 series endpoint.
* **DAX Formula:**
```dax
Último Rótulo Top 5 = 
VAR UltimaData = 
    MAXX(
        FILTER(
            ALLSELECTED(dim_calendario[data]),
            NOT ISBLANK(CALCULATE([Mediana Top 5]))
        ),
        dim_calendario[data]
    )
RETURN
    IF(
        SELECTEDVALUE(dim_calendario[data]) = UltimaData,
        FORMAT([Mediana Top 5], "0.00", "pt-BR") & "%",
        BLANK()
    )
```

### 5.11 `Último Rótulo Mercado`
* **Purpose:** Formatted string percentage (`0.00%`) on the Market series endpoint.
* **DAX Formula:**
```dax
Último Rótulo Mercado = 
VAR UltimaData = 
    MAXX(
        FILTER(
            ALLSELECTED(dim_calendario[data]),
            NOT ISBLANK(CALCULATE([Mediana Mercado Comparativo]))
        ),
        dim_calendario[data]
    )
RETURN
    IF(
        SELECTEDVALUE(dim_calendario[data]) = UltimaData,
        FORMAT([Mediana Mercado Comparativo], "0.00", "pt-BR") & "%",
        BLANK()
    )
```

### 5.12 `Ponteiro Top 5`
* **Purpose:** Numeric value on the latest date to plot circular highlight marker on Top 5 line.
* **DAX Formula:**
```dax
Ponteiro Top 5 = 
VAR UltimaData = 
    MAXX(
        FILTER(
            ALLSELECTED(dim_calendario[data]),
            NOT ISBLANK(CALCULATE([Mediana Top 5]))
        ),
        dim_calendario[data]
    )
RETURN
    IF(
        SELECTEDVALUE(dim_calendario[data]) = UltimaData,
        [Mediana Top 5],
        BLANK()
    )
```

### 5.13 `Ponteiro Mercado`
* **Purpose:** Numeric value on the latest date to plot circular highlight marker on Market line.
* **DAX Formula:**
```dax
Ponteiro Mercado = 
VAR UltimaData = 
    MAXX(
        FILTER(
            ALLSELECTED(dim_calendario[data]),
            NOT ISBLANK(CALCULATE([Mediana Mercado Comparativo]))
        ),
        dim_calendario[data]
    )
RETURN
    IF(
        SELECTEDVALUE(dim_calendario[data]) = UltimaData,
        [Mediana Mercado Comparativo],
        BLANK()
    )
```

---

## 6. Page 3: Interest Rates & Inflation (Fisher Equation)

### 6.1 `KPI Juro Real Ex-Ante`
* **Purpose:** Fisher real rate on the latest observation date, disregarding calendar filters.
* **DAX Formula:**
```dax
KPI Juro Real Ex-Ante = 
VAR DataMax = CALCULATE(MAX(fct_juro_real_ex_ante[data]), REMOVEFILTERS(dim_calendario))
RETURN
CALCULATE(
    AVERAGE(fct_juro_real_ex_ante[taxa_juro_real_ex_ante]),
    fct_juro_real_ex_ante[data] = DataMax
)
```

### 6.2 `KPI Selic Vigente`
* **Purpose:** Effective annual Selic target rate from series SGS 432 on the latest observation date.
* **DAX Formula:**
```dax
KPI Selic Vigente = 
VAR DataMax = CALCULATE(MAX(fct_juro_real_ex_ante[data]), REMOVEFILTERS(dim_calendario))
RETURN
CALCULATE(
    AVERAGE(fct_juro_real_ex_ante[taxa_selic_meta_aa]),
    fct_juro_real_ex_ante[data] = DataMax
)
```

### 6.3 `KPI Inflação 12M`
* **Purpose:** Smoothed expected 12-month forward IPCA inflation on the latest observation date.
* **DAX Formula:**
```dax
KPI Inflação 12M = 
VAR DataMax = CALCULATE(MAX(fct_juro_real_ex_ante[data]), REMOVEFILTERS(dim_calendario))
RETURN
CALCULATE(
    AVERAGE(fct_juro_real_ex_ante[ipca_esperado_12m]),
    fct_juro_real_ex_ante[data] = DataMax
)
```

### 6.4 `Juro Real Histórico`
* **Purpose:** Continuous long-term time series for ex-ante real rate line chart.
* **DAX Formula:**
```dax
Juro Real Histórico = 
AVERAGE(fct_juro_real_ex_ante[taxa_juro_real_ex_ante])
```

### 6.5 `Selic Histórica`
* **Purpose:** Continuous daily target Selic rate series.
* **DAX Formula:**
```dax
Selic Histórica = 
AVERAGE(fct_juro_real_ex_ante[taxa_selic_meta_aa])
```

### 6.6 `Inflação 12M Histórica`
* **Purpose:** Continuous expected 12-month forward IPCA inflation series.
* **DAX Formula:**
```dax
Inflação 12M Histórica = 
AVERAGE(fct_juro_real_ex_ante[ipca_esperado_12m])
```

### 6.7 `Ponteiro Juro Real`
* **Purpose:** Pointers isolate the series endpoint for highlight markers on Real Interest Rate curve.
* **DAX Formula:**
```dax
Ponteiro Juro Real = 
VAR UltimaData = 
    MAXX(
        FILTER(
            ALLSELECTED(dim_calendario[data]),
            NOT ISBLANK(CALCULATE([Juro Real Histórico]))
        ),
        dim_calendario[data]
    )
RETURN
IF(SELECTEDVALUE(dim_calendario[data]) = UltimaData, [Juro Real Histórico], BLANK())
```

### 6.8 `Ponteiro Selic Vigente`
* **Purpose:** Pointers isolate the series endpoint for highlight markers on Selic curve.
* **DAX Formula:**
```dax
Ponteiro Selic Vigente = 
VAR UltimaData = 
    MAXX(
        FILTER(
            ALLSELECTED(dim_calendario[data]),
            NOT ISBLANK(CALCULATE([Selic Histórica]))
        ),
        dim_calendario[data]
    )
RETURN
IF(SELECTEDVALUE(dim_calendario[data]) = UltimaData, [Selic Histórica], BLANK())
```

### 6.9 `Ponteiro Inflação 12M`
* **Purpose:** Pointers isolate the series endpoint for highlight markers on Inflation 12M curve.
* **DAX Formula:**
```dax
Ponteiro Inflação 12M = 
VAR UltimaData = 
    MAXX(
        FILTER(
            ALLSELECTED(dim_calendario[data]),
            NOT ISBLANK(CALCULATE([Inflação 12M Histórica]))
        ),
        dim_calendario[data]
    )
RETURN
IF(SELECTEDVALUE(dim_calendario[data]) = UltimaData, [Inflação 12M Histórica], BLANK())
```
