# How-to: Executar e Testar os Modelos dbt no Microsoft Fabric

Este guia fornece instruções passo a passo para compilar, executar transformações e validar testes de integridade e qualidade de dados utilizando o **dbt (Data Build Tool)** integrado ao **Microsoft Fabric**.

---

## Objetivo
Executar os modelos dimensionais da camada **Gold** e rodar testes automatizados de chaves primárias, nulidade e relacionamentos referenciais.

---

## Estrutura do Projeto dbt

O projeto dbt está localizado em `fabric/05 - dbt/dbt_focus_intelligence.DataBuildToolJob/Code/dbt` e possui a seguinte arquitetura:

* **Sources (`models/gold/sources.yml`):** Apontam para as tabelas Delta da camada Silver (`silver_focus_anuais`, `silver_focus_top5_anuais`, `silver_focus_inflacao_12m`, `silver_sgs_selic_meta`).
* **Modelos Dimensionais (`models/gold/`):**
  * `dim_calendario.sql`: Tabela de tempo de 2000 a 2035 com granularidade diária.
  * `dim_indicador.sql`: Metadados e unidades de medida dos indicadores.
  * `fct_expectativas_mercado.sql`: Fato das projeções anuais do consenso geral do mercado.
  * `fct_comparativo_top5.sql`: Fato comparando Mercado vs Top 5 e calculando a divergência (spread).
  * `fct_juro_real_ex_ante.sql`: Fato calculando a taxa de juro real diária via Equação de Fisher.

---

## Como Executar no Microsoft Fabric

### Método 1: Pela Interface Web do Fabric (Recomendado)
1. No seu Workspace do Fabric, localize o item do tipo **dbt Job** com o nome **`dbt_focus_intelligence`**.
2. Clique no job para abrir a interface do editor dbt no Fabric.
3. No menu superior, utilize os botões rápidos:
   * **Run:** Executa os comandos padrão (`dbt run`).
   * **Test:** Executa os testes de esquema (`dbt test`).
4. Para executar a esteira completa (compilação, execução e testes em um único comando):
   No console inferior, digite:
   ```bash
   dbt build
   ```
5. Acompanhe os logs em tempo real na aba de saída.

---

### Método 2: Executar Apenas um Modelo Específico
Se você modificou apenas a lógica da Equação de Fisher ou o comparativo Top 5:
* Para rodar apenas o modelo de juro real:
  ```bash
  dbt run --select fct_juro_real_ex_ante
  ```
* Para rodar o modelo e todos os modelos que dependem dele:
  ```bash
  dbt run --select fct_comparativo_top5+
  ```

---

## Validar Testes de Qualidade de Dados (dbt Test)

O arquivo `models/gold/schema.yml` possui regras formais de validação configuradas:

| Tabela | Testes Aplicados | Objetivo do Teste |
| :--- | :--- | :--- |
| **dim_calendario** | `unique`, `not_null` em `data_sk` e `data` | Garante que não há datas duplicadas ou nulas no calendário. |
| **dim_indicador** | `unique`, `not_null` em `indicador_id` e `indicador` | Assegura unicidade no catálogo de indicadores. |
| **fct_expectativas_mercado**| `not_null`, `relationships` para `dim_calendario` | Garante integridade referencial com a dimensão de tempo. |
| **fct_comparativo_top5** | `not_null`, `relationships` para `dim_calendario` | Impede registros órfãos sem data correspondente. |
| **fct_juro_real_ex_ante** | `not_null`, `relationships` para `dim_calendario` | Valida que todo cálculo de juro real possui data válida. |

Para rodar todos os testes:
```bash
dbt test
```

Se todos os testes passarem, a saída final exibirá:
```text
Finished running 18 data tests ...
Completed successfully
Done. PASS=18 WARN=0 ERROR=0 SKIP=0 TOTAL=18
```

---

## Resolução de Problemas Comuns (Troubleshooting)

### 1. Erro: `Source 'lakehouse_silver.silver_...' does not exist`
* **Causa:** O notebook `nb_02_bronze_to_silver` ainda não foi executado ou a tabela Silver não foi criada no Lakehouse `lk_focus_intelligence`.
* **Solução:** Execute o notebook `nb_02_bronze_to_silver` antes de rodar o dbt, ou dispare a pipeline `pl_focus_market_intelligence`.

### 2. Erro de sintaxe T-SQL ou arredondamento
* **Causa:** O Fabric Warehouse utiliza sintaxe T-SQL / SQL Server.
* **Solução:** Verifique se as funções de data utilizam `CONVERT(VARCHAR(8), data, 112)` e casting explícito de ponto flutuante `(1.0 + (taxa / 100.0))` para evitar truncamento de inteiros.
