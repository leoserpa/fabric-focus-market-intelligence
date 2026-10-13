# Tutorial: Inicialização do Ambiente do Zero (Primeiros Passos)

Este tutorial orienta você no processo completo de replicação do projeto **Focus Market Intelligence** em um novo Workspace do **Microsoft Fabric**, desde a sincronização com o Git até a primeira execução da pipeline de dados e visualização do relatório no Power BI.

---

## Objetivo
Ao final deste tutorial, você terá:
1. Um Workspace no Microsoft Fabric conectado ao repositório GitHub.
2. Todas as tabelas das camadas Bronze, Silver e Gold criadas e populadas.
3. Os modelos do dbt compilados e validados no Fabric Warehouse.
4. O relatório do Power BI com as 3 páginas funcionando em tempo real via Direct Lake.

**Tempo estimado:** 25 a 35 minutos.

---

## Pré-requisitos
Antes de começar, certifique-se de ter:
* Uma conta ativa no **Microsoft Fabric** com acesso a uma capacidade (capacidade de teste **Fabric Trial** ou capacidade paga **F2+**).
* Permissão de Administrador ou Membro no Workspace do Fabric.
* Uma conta no **GitHub** com acesso de escrita a este repositório.

---

## Passo a Passo

### Etapa 1: Criar o Workspace no Microsoft Fabric
1. Acesse o portal oficial: [app.fabric.microsoft.com](https://app.fabric.microsoft.com).
2. No menu lateral esquerdo, clique em **Workspaces** (Espaços de trabalho) > **Novo espaço de trabalho**.
3. Defina um nome para o workspace (ex: `WS_FOCUS_MARKET_INTELLIGENCE`).
4. Em **Avançado**, certifique-se de associar o workspace a uma **Capacidade do Fabric** (Trial ou Dedicada).
5. Clique em **Aplicar**.

---

### Etapa 2: Conectar o Workspace ao Git (Controle de Código-Fonte)
O Microsoft Fabric possui integração nativa com o GitHub.
1. No menu superior do seu novo workspace, clique em **Configurações do espaço de trabalho**.
2. Acesse a aba **Integração do Git**.
3. Preencha as credenciais e parâmetros:
   * **Provedor:** GitHub
   * **Organização / Usuário:** Seu usuário do GitHub
   * **Repositório:** Nome do repositório clonado ou com fork
   * **Ramificação (Branch):** `main`
   * **Pasta do Git:** Digite `/fabric` *(atenção à barra inicial: os artefatos do Fabric estão dentro dessa pasta)*.
4. Clique em **Conectar e sincronizar**.
5. O Fabric exibirá a tela de sincronização inicial. Selecione a opção para carregar os artefatos da branch remota para o workspace e confirme.

> **Resultado:** Os seguintes artefatos aparecerão na lista do workspace:
> * `lk_focus_intelligence` (Lakehouse)
> * `nb_01_raw_to_bronze` e `nb_02_bronze_to_silver` (Notebooks)
> * `pl_focus_market_intelligence` (Data Pipeline)
> * `wh_focus_intelligence` (Warehouse)
> * `dbt_focus_intelligence` (dbt Job)
> * `sm_focus_market_intelligence` (Semantic Model)
> * `rpt_focus_market_intelligence` (Power BI Report)

#### Exibição de Linhagem do Workspace (Lineage View)
Ao alternar a visualização do workspace para a **Exibição de Linhagem** (*Lineage View*), você verá a topologia de conexão entre os artefatos sincronizados:

![Exibição de Linhagem do Workspace no Microsoft Fabric](../../assets/screenshots/05-linhagem-workspace-fabric.png)

---

### Etapa 3: Executar a Pipeline de Ingestão e Processamento
Para popular as tabelas e transformar os dados pela primeira vez:
1. Na lista de itens do workspace, clique na pipeline **`pl_focus_market_intelligence`**.
2. No menu superior da pipeline, clique no botão **Executar** (*Run*).
3. A pipeline executará as etapas na seguinte ordem automatizada:
   * **Atividade 1 (`ingestao_bronze_bcb`):** Executa o notebook `nb_01_raw_to_bronze` (consome a API Olinda do BCB e a série SGS 432 com janela de tolerância de 30 dias, gravando as tabelas brutas no Lakehouse Bronze).
   * **Atividade 2 (`aguardar_liberacao_spark`):** Atividade de espera (*Wait*) de 60 segundos. Atua como buffer de estabilização para desalocação de nós e liberação de capacidade de computação Spark no Microsoft Fabric, mitigando concorrência e saturação de capacidade (erro HTTP 430) em capacidades F/Trial.
   * **Atividade 3 (`curacao_silver_delta`):** Executa o notebook `nb_02_bronze_to_silver` (padroniza tipagens, formata datas, aplica deduplicação e regras de negócio para o Lakehouse Silver).
   * **Atividade 4 (`modelagem_gold_dbt`):** Dispara o job do dbt `dbt_focus_intelligence` (compila e materializa o esquema estrela dimensional no Data Warehouse via T-SQL e executa a suíte de testes de integridade).
4. Aguarde até que todas as atividades apresentem status de êxito (*Succeeded*):

![Execução Bem-Sucedida da Pipeline no Microsoft Fabric](../../assets/screenshots/06-execucao-pipeline-fabric.png)

---

### Etapa 4: Validar os Dados no Warehouse
1. Retorne à raiz do workspace e abra o Warehouse **`wh_focus_intelligence`**.
2. No painel de navegação esquerdo, expanda o schema **`gold`**.
3. Confirme a presença e consulte as tabelas geradas:
   ```sql
   SELECT TOP 10 * FROM gold.fct_juro_real_ex_ante ORDER BY data DESC;
   SELECT TOP 10 * FROM gold.fct_comparativo_top5 ORDER BY data DESC;
   SELECT TOP 10 * FROM gold.fct_expectativas_mercado ORDER BY data DESC;
   ```

---

### Etapa 5: Abrir e Interagir com o Relatório Power BI
1. No workspace, clique no relatório **`rpt_focus_market_intelligence`**.
2. O relatório abrirá com os 3 painéis dinâmicos:
   * **Página 1 (Panorama Focus):** Curvas de IPCA, Selic, PIB e Dólar com destaque dos últimos 30 dias.
   * **Página 2 (Mercado x Top 5):** Análise de divergência e dispersão hawkish/dovish.
   * **Página 3 (Juros e inflação):** Curva contínua do Juro Real Ex-Ante pela Equação de Fisher e decisões do Copom.
3. Verifique se o selo no canto superior direito indica a data da observação mais recente (ex: `02/10/2026`).

#### Visão dos Painéis Executivos no Power BI:

**Página 1: Panorama Focus**
![Página 1 - Panorama Focus](../../assets/screenshots/01-panorama-focus.jpg)

**Página 2: Mercado x Top 5**
![Página 2 - Mercado x Top 5](../../assets/screenshots/02-mercado-top5.jpg)

**Página 3: Juros e Inflação (Juro Real Ex-Ante)**
![Página 3 - Juros e Inflação](../../assets/screenshots/03-juros-inflacao.jpg)

---

## Conclusão
Você replicou com sucesso uma infraestrutura corporativa de Analytics Engineering no Microsoft Fabric.

**Próximos passos recomendados:**
* Para entender as transformações e testes de dados, leia o guia [Como Executar e Testar Modelos dbt](../guias-praticos/executar-pipeline-dbt.md).
* Para compreender as fórmulas econômicas e a arquitetura em detalhes, leia [Metodologia Focus e Equação de Fisher](../explicacao/metodologia-focus-e-fisher.md).
