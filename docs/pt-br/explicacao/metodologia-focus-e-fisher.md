# Explicação: Metodologia Focus e Equação de Fisher

Este documento detalha os fundamentos teóricos, macroeconômicos e matemáticos que sustentam a análise do **Focus Market Intelligence**, com ênfase na coleta do Banco Central do Brasil e na dedução rigorosa da **taxa de juro real ex-ante**.

---

## O Sistema de Expectativas de Mercado do Banco Central (Focus)

O Banco Central do Brasil (BCB) monitora diariamente as expectativas de mercado por meio de um sistema automatizado que coleta projeções de mais de uma centena de bancos, corretoras, consultorias e gestoras de recursos.

### Frequência de Apuração: Diária vs Semanal
* **Boletim Focus (PDF Semanal):** Publicado toda segunda-feira pela manhã, consolida a visão das instituições na sexta-feira anterior.
* **API Olinda (Série Diária em Dias Úteis):** O banco de dados do BCB apura e publica os dados com granularidade de **dias úteis**. As instituições atualizam seus modelos continuamente, permitindo acompanhar inflexões no consenso dia a dia.

### As Bases de Cálculo do BCB
1. **Base 0 (Janela de 30 dias corridos):** Utilizada no *Panorama Focus* (Página 1). Considera as respostas atualizadas pelas instituições participantes nos últimos 30 dias para o ano civil de referência (ex: encerramento de 2026).
2. **Base 1 (Janela de 5 dias úteis):** Utilizada na taxa de juro real e na inflação de 12 meses (Página 3). Considera apenas as informações mais recentes fornecidas nos últimos 5 dias úteis, garantindo sensibilidade imediata a notícias e choques econômicos.

---

## O Grupo Top 5: Quem é e Como Funciona

O Banco Central ranqueia periodicamente as instituições financeiras com os maiores índices de acerto em suas projeções econômicas (IPCA, Selic, Câmbio e IGP-M).
* As **Top 5** são as 5 instituições mais precisas do país.
* **Relevância para a tomada de decisão:** A comparação entre o Consenso Geral e o Top 5 revela a presença de viés de ancoragem ou antecipação de movimentos de mercado. Se o Top 5 estiver substancialmente mais agressivo (*hawkish*) que a média, o mercado frequentemente ajusta suas apostas nas semanas seguintes.

---

## A Equação de Fisher: Rigor no Juro Real Ex-Ante

A taxa de juro real é a taxa de juros nominal descontada da taxa de inflação esperada. A formulação matemática clássica desenvolvida pelo economista Irving Fisher estabelece:

$$(1 + i) = (1 + r)(1 + \pi^e)$$

Onde:
* $i$ = Taxa de juros nominal vigente (% a.a.) — Meta da taxa Selic definida pelo Copom.
* $r$ = Taxa de juro real ex-ante (% a.a.).
* $\pi^e$ = Taxa de inflação esperada para os próximos 12 meses (% a.a.) — IPCA 12M suavizado do Focus.

Isolando a taxa real $r$:

$$r = \left( \frac{1 + \frac{i}{100}}{1 + \frac{\pi^e}{100}} - 1 \right) \times 100$$

---

### Por que a aproximação linear ($r \approx i - \pi$) é proibida em economias como o Brasil?

Em economias desenvolvidas com juros nominais e inflação próximos de 2%, analistas costumam usar a subtração linear simples ($r \approx i - \pi$). 

No entanto, no Brasil, com taxas nominais de dois dígitos, a subtração linear gera uma **distorção inaceitável**:

#### Exemplo Prático com os Dados do Projeto (Outubro/2026):
* **Selic Vigente ($i$):** $13,75\%$
* **Inflação Esperada 12M ($\pi^e$):** $4,65\%$

1. **Subtração Linear Simplista:**
   $$r_{\text{linear}} = 13,75\% - 4,65\% = \mathbf{9,10\%}$$

2. **Equação de Fisher Exata (Implementada no dbt e no Dashboard):**
   $$r_{\text{Fisher}} = \left( \frac{1 + 0,1375}{1 + 0,0465} - 1 \right) \times 100 = \left( \frac{1,1375}{1,0465} - 1 \right) \times 100 = \mathbf{8,6956\% \approx 8,69\%}$$

> **Impacto:** A subtração linear superestimaria a taxa de juro real brasileira em **+0,41 ponto percentual (41 basis points)**. Em avaliação de risco soberano, custo de capital (WACC) e precificação de títulos públicos (NTN-B), um erro de 41 bps distorce o valuation e o retorno real do investidor.

---

## Por que "Ex-Ante"?
* **Juro Real Ex-Post:** Olha pelo retrovisor. Desconta a inflação passada que já ocorreu. Útil para verificar o retorno histórico realizado.
* **Juro Real Ex-Ante:** Olha para o para-brisa. Desconta a inflação que o mercado **espera** que ocorra nos próximos 12 meses. É a métrica relevante que baliza as decisões de política monetária do Copom, o aperto das condições financeiras e o investimento produtivo das empresas.
