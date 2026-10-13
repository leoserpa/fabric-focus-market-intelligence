# Referência: Catálogo Completo de Medidas DAX

Este documento cataloga formalmente todas as **40 medidas DAX** implementadas na tabela `_Medidas` do modelo semântico **`sm_focus_market_intelligence`** ([_Medidas.tmdl](../../../fabric/06%20-%20Semantic%20Models/sm_focus_market_intelligence.SemanticModel/definition/tables/_Medidas.tmdl)), detalhando sua fórmula exata, propósito de negócio, comportamento em tela e formatação.

---

## Sumário Executivo das Medidas

| Categoria | Quantidade | Finalidade Principal |
| :--- | :---: | :--- |
| **1. Cabeçalho e Metadados Dinâmicos** | 2 | Selo de atualização temporal com números em Unicode negrito nativo e data máxima. |
| **2. Métricas Base de Projeção** | 5 | Agregações fundamentais de mercado, Top 5, spreads, taxas Selic e Fisher. |
| **3. Página 1: Panorama Focus (Linhas e Destaque)** | 6 | Gráfico contínuo bicolor (últimos 30 dias em laranja) e isolamento de rótulos finais. |
| **4. Página 1: KPIs Executivos (Ano 2026)** | 5 | Mediana isolada da data mais recente para IPCA, Selic, PIB Total e Câmbio. |
| **5. Página 2: Mercado x Top 5 (Divergência)** | 13 | Spreads institucionais Hawkish/Dovish, cores condicionais HEX, rótulos e marcadores. |
| **6. Página 3: Juros e Inflação (Fisher e Selic)** | 9 | Curvas contínuas de juro real e Selic diária, KPIs pontuais e marcadores finais. |
| **Total** | **40** | **Todas as medidas em produção no modelo semântico Direct Lake.** |

---

## 1. Cabeçalho e Metadados Dinâmicos

### 1.1 `Texto Observação Mais Recente`
* **Propósito:** Monta a string do selo dinâmico no topo de todas as páginas do relatório, identificando a data da observação mais recente entre as 3 tabelas fatos. Converte os números da data para numerais em negrito nativo Unicode (`𝟬` a `𝟵`), garantindo tipografia destacada sem depender de HTML customizado.
* **Fórmula DAX:**
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

-- Converte cada número para negrito real nativo via Unicode
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
* **Propósito:** Retorna a data escalar mais recente registrada na tabela `fct_expectativas_mercado`, ignorando filtros externos da dimensão calendário.
* **Fórmula DAX:**
```dax
Última Data Focus = 
CALCULATE(
    MAX(fct_expectativas_mercado[data]),
    REMOVEFILTERS(dim_calendario[data])
)
```

---

## 2. Métricas Base de Projeção

### 2.1 `Mediana Mercado`
* **Propósito:** Calcula a mediana do consenso geral de mercado na tabela `fct_expectativas_mercado` no contexto de filtro ativo.
* **Fórmula DAX:**
```dax
Mediana Mercado = 
AVERAGE(fct_expectativas_mercado[mediana])
```

### 2.2 `Mediana Top 5`
* **Propósito:** Calcula a mediana do grupo Top 5 (médio prazo) na tabela `fct_comparativo_top5`.
* **Fórmula DAX:**
```dax
Mediana Top 5 = 
AVERAGE(fct_comparativo_top5[mediana_top5])
```

### 2.3 `Divergência Top 5`
* **Propósito:** Diferença direta entre o consenso do Top 5 e o consenso geral do mercado ($\text{Top 5} - \text{Mercado}$).
* **Fórmula DAX:**
```dax
Divergência Top 5 = 
[Mediana Top 5] - [Mediana Mercado]
```

### 2.4 `Juro Real Ex-Ante`
* **Propósito:** Retorna a taxa diária de juro real calculada rigorosamente pela Equação de Fisher no Warehouse.
* **Fórmula DAX:**
```dax
Juro Real Ex-Ante = 
SELECTEDVALUE(fct_juro_real_ex_ante[taxa_juro_real_ex_ante])
```

### 2.5 `Selic Atual`
* **Propósito:** Retorna a taxa meta Selic anualizada vigente da tabela de juro real no contexto diário.
* **Fórmula DAX:**
```dax
Selic Atual = 
SELECTEDVALUE(fct_juro_real_ex_ante[taxa_selic_meta_aa])
```

---

## 3. Página 1: Panorama Focus (Linhas e Destaque 30 Dias)

### 3.1 `Data Início Destaque`
* **Propósito:** Localiza a data da última observação válida no gráfico e subtrai exatamente 30 dias para delimitar a janela recente de destaque visual.
* **Fórmula DAX:**
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
* **Propósito:** Alimenta o segmento histórico da linha (cor cinza suave `#A4AAAD`), retornando valores apenas para datas anteriores ou iguais à data de início do destaque.
* **Fórmula DAX:**
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
* **Propósito:** Alimenta o segmento recente da linha (cor laranja institucional `#FA590B`), retornando valores apenas para datas a partir do corte de 30 dias.
* **Fórmula DAX:**
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
* **Propósito:** Retorna a mediana numérica apenas no último ponto da série temporal, permitindo renderizar o marcador final sem poluição visual no gráfico.
* **Fórmula DAX:**
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
* **Propósito:** Rótulo de texto formatado como percentual com duas casas decimais no padrão brasileiro (`0.00%`) exclusivamente no último ponto da linha (IPCA, Selic, PIB).
* **Fórmula DAX:**
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
* **Propósito:** Rótulo de texto formatado como moeda brasileira (`R$ 0.00`) exclusivamente no último ponto da curva de Dólar/Câmbio.
* **Fórmula DAX:**
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

## 4. Página 1: KPIs Executivos (Ano Referência 2026)

### 4.1 `KPI Última Mediana`
* **Propósito:** Medida de base para os cartões executivos; recupera a mediana do mercado na data mais recente desconsiderando seleções do filtro de calendário.
* **Fórmula DAX:**
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
* **Propósito:** Retorna a última projeção do IPCA anual de 2026 sob apuração de Base 0.
* **Fórmula DAX:**
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
* **Propósito:** Retorna a última projeção da taxa Selic anual de 2026 sob apuração de Base 0.
* **Fórmula DAX:**
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
* **Propósito:** Retorna a última projeção de crescimento do PIB Total de 2026 sob apuração de Base 0.
* **Fórmula DAX:**
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
* **Propósito:** Retorna a última projeção de taxa de Câmbio (USD/BRL) para o encerramento de 2026 sob apuração de Base 0.
* **Fórmula DAX:**
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

## 5. Página 2: Mercado x Top 5 (Análise de Divergência)

### 5.1 `Mediana Mercado Comparativo`
* **Propósito:** Mediana do consenso geral presente na tabela comparativa `fct_comparativo_top5`.
* **Fórmula DAX:**
```dax
Mediana Mercado Comparativo = 
AVERAGE(fct_comparativo_top5[mediana_mercado])
```

### 5.2 `Divergência Top 5 Spread`
* **Propósito:** Média do campo `divergencia_top5_mercado`, quantificando o spread em pontos percentuais entre o grupo Top 5 e o Mercado.
* **Fórmula DAX:**
```dax
Divergência Top 5 Spread = 
AVERAGE(fct_comparativo_top5[divergencia_top5_mercado])
```

### 5.3 `Cor da Divergência`
* **Propósito:** Regra de formatação condicional HEX para gráficos de colunas: Laranja (`#E66C37`) para postura Hawkish ($\ge 0$) e Cinza grafite (`#A4AAAD`) para Dovish ($< 0$).
* **Fórmula DAX:**
```dax
Cor da Divergência = 
IF(
    [Divergência Top 5 Spread] >= 0,
    "#E66C37",  -- Laranja (Top 5 mais alto / Hawkish)
    "#A4AAAD"   -- Cinza escuro (Top 5 mais baixo / Dovish)
)
```

### 5.4 `KPI Divergência IPCA`
* **Propósito:** Spread pontual entre Top 5 e Mercado para o IPCA 2026 na data mais recente observada.
* **Fórmula DAX:**
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
* **Propósito:** Spread pontual entre Top 5 e Mercado para a Selic 2026 na data mais recente observada.
* **Fórmula DAX:**
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
* **Propósito:** Mediana do consenso geral avaliada na data global mais recente da tabela comparativa.
* **Fórmula DAX:**
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
* **Propósito:** Mediana do grupo Top 5 avaliada na data global mais recente da tabela comparativa.
* **Fórmula DAX:**
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
* **Propósito:** Spread institucional na data mais recente para alimentar matrizes e tabelas analíticas.
* **Fórmula DAX:**
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
* **Propósito:** Formatação condicional para matriz de dados: Laranja (`#E66C37`) para spread positivo, Grafite (`#23282B`) para negativo e Cinza neutro (`#8C969A`) para spread zero.
* **Fórmula DAX:**
```dax
Cor da Diferença Tabela = 
VAR Dif = [Divergência Última Data]
RETURN
SWITCH(
    TRUE(),
    Dif > 0, "#E66C37",   -- Laranja institucional Focus
    Dif < 0, "#23282B",   -- Grafite escuro
    "#8C969A"             -- Cinza suave para o 0,00 (Consenso)
)
```

### 5.10 `Último Rótulo Top 5`
* **Propósito:** Rótulo formatado em percentual (`0.00%`) no último ponto da curva do Top 5.
* **Fórmula DAX:**
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
* **Propósito:** Rótulo formatado em percentual (`0.00%`) no último ponto da curva do Mercado no comparativo.
* **Fórmula DAX:**
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
* **Propósito:** Retorna o valor numérico apenas na última data para fixação de marcador circular no gráfico de linha do Top 5.
* **Fórmula DAX:**
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
* **Propósito:** Retorna o valor numérico apenas na última data para fixação de marcador circular no gráfico de linha do Mercado.
* **Fórmula DAX:**
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

## 6. Página 3: Juros e Inflação (Equação de Fisher)

### 6.1 `KPI Juro Real Ex-Ante`
* **Propósito:** Taxa de juro real ex-ante calculada pela Equação de Fisher na data de observação mais recente, sem filtros de calendário.
* **Fórmula DAX:**
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
* **Propósito:** Meta Selic anualizada oficial fixada pelo Copom (série SGS 432) na data de observação mais recente.
* **Fórmula DAX:**
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
* **Propósito:** Expectativa de inflação IPCA suavizada para os próximos 12 meses móveis na data mais recente.
* **Fórmula DAX:**
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
* **Propósito:** Série temporal contínua da taxa de juro real ex-ante para o gráfico de linhas de longo prazo.
* **Fórmula DAX:**
```dax
Juro Real Histórico = 
AVERAGE(fct_juro_real_ex_ante[taxa_juro_real_ex_ante])
```

### 6.5 `Selic Histórica`
* **Propósito:** Série temporal contínua da taxa Selic meta anualizada.
* **Fórmula DAX:**
```dax
Selic Histórica = 
AVERAGE(fct_juro_real_ex_ante[taxa_selic_meta_aa])
```

### 6.6 `Inflação 12M Histórica`
* **Propósito:** Série temporal contínua da expectativa de inflação IPCA em 12 meses.
* **Fórmula DAX:**
```dax
Inflação 12M Histórica = 
AVERAGE(fct_juro_real_ex_ante[ipca_esperado_12m])
```

### 6.7 `Ponteiro Juro Real`
* **Propósito:** Valor escalar no último ponto da série para renderização de marcador destacado na curva de Juro Real.
* **Fórmula DAX:**
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
* **Propósito:** Valor escalar no último ponto da série para renderização de marcador destacado na curva da taxa Selic.
* **Fórmula DAX:**
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
* **Propósito:** Valor escalar no último ponto da série para renderização de marcador destacado na curva de inflação IPCA 12M.
* **Fórmula DAX:**
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
