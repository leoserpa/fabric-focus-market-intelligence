# Referência: Catálogo de Medidas DAX

Este documento cataloga formalmente as medidas DAX implementadas na tabela `_Medidas` do modelo semântico **`sm_focus_market_intelligence`**, explicando sua lógica de cálculo, propósito analítico e formatação.

---

## 1. Medidas de Cabeçalho e Atualização

### `Última Data da Observação`
Retorna a data mais recente disponível entre as 3 tabelas fatos do modelo, garantindo atualização dinâmica mesmo se uma das séries for atualizada em horário distinto.
```dax
Última Data da Observação = 
VAR DataFocus = CALCULATE(MAX(fct_expectativas_mercado[data]), REMOVEFILTERS())
VAR DataTop5  = CALCULATE(MAX(fct_comparativo_top5[data]), REMOVEFILTERS())
VAR DataJuros = CALCULATE(MAX(fct_juro_real_ex_ante[data]), REMOVEFILTERS())
RETURN MAX(DataFocus, MAX(DataTop5, DataJuros))
```

### `HTML Observação Mais Recente`
Gera a estrutura visual do selo de atualização para o visual customizado *HTML Content*, exibindo o texto descritivo em `#626E73` e a data em negrito escuro `#23282B`.
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

## 2. Medidas da Página 1 (Panorama Focus)

### `KPI IPCA 2026`, `KPI Selic 2026`, `KPI PIB 2026`, `KPI Câmbio 2026`
Calculam a mediana do mercado geral na data de corte mais recente para cada indicador do ano de 2026.
* Formatos: `0.00%` para IPCA, Selic e PIB; `R$ #,0.00` para Câmbio.

### `Data Início Destaque`
Calcula a data exata de corte para a janela dos **últimos 30 dias** com base na última observação com dados válidos:
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

### `Mediana Histórico` e `Mediana Recente`
Permitem colorir a linha com duas cores distintas sem quebra de continuidade:
* **`Mediana Histórico`:** Retorna valor se `data <= [Data Início Destaque]` (linha cinza `#A4AAAD`).
* **`Mediana Recente`:** Retorna valor se `data >= [Data Início Destaque]` (linha laranja `#FA590B`).

### `Último Valor do Gráfico`
Retorna a mediana apenas na última data selecionada para renderizar o ponto final e o rótulo de dados no gráfico de linha, eliminando poluição visual.

---

## 3. Medidas da Página 2 (Mercado x Top 5)

### `Delta IPCA 2026` e `Delta Selic 2026`
Mede a divergência entre Top 5 e o Mercado geral para o ano de 2026:
$$\Delta = \text{Mediana Top 5} - \text{Mediana Mercado}$$
* Formatado como `+0,00 p.p.` ou `-0,22 p.p.` com o símbolo Delta.

### `Cor Spread IPCA`
Regra de formatação condicional para o gráfico de colunas de divergência:
* Se `divergência > 0` (Top 5 mais hawkish que o mercado): Laranja institucional `#FA590B`.
* Se `divergência <= 0` (Top 5 neutro ou dovish): Cinza grafite `#626E73`.

---

## 4. Medidas da Página 3 (Juros e Inflação)

### `KPI Juro Real Ex-Ante`
Mede a taxa de juro real ex-ante calculada pela Equação de Fisher na data de observação mais recente:
```dax
KPI Juro Real Ex-Ante = 
VAR DataMax = CALCULATE(MAX(fct_juro_real_ex_ante[data]), REMOVEFILTERS(dim_calendario))
RETURN
CALCULATE(
    AVERAGE(fct_juro_real_ex_ante[taxa_juro_real_ex_ante]),
    fct_juro_real_ex_ante[data] = DataMax
)
```
* Formatação: `0.00%` (ex: `8,69%`).

### `KPI Selic Vigente`
Meta oficial do Copom fixada na série SGS 432 na data mais recente.
* Formatação: `0.00%` (ex: `13,75%`).

### `KPI Inflação 12M`
Mediana do IPCA suavizado em horizonte de 12 meses (Base 1 - 5 dias úteis) na data mais recente.
* Formatação: `0.00%` (ex: `4,65%`).

### Ponteiros de Linha (`Ponteiro Juro Real`, `Ponteiro Selic Vigente`, `Ponteiro Inflação 12M`)
Filtram os valores exclusivamente no último dia útil disponível da série temporal de 6 meses, projetando o marcador circular e o rótulo em laranja sobre as trajetórias monocromáticas em cinza `#A4AAAD`.
