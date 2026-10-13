# Guia Prático: Sincronizar o Microsoft Fabric com o GitHub (Integração Git)

Este guia ensina como utilizar o recurso de **Controle de Código-Fonte (Integração Git)** do **Microsoft Fabric** para versionar modelos semânticos, relatórios e pipelines diretamente no GitHub com rastreabilidade.

---

## Objetivo
Aprender a salvar alterações feitas no Fabric (Power BI, DAX, Pipelines, Notebooks), criar commits atômicos e manter o repositório sincronizado.

---

## Como Funciona o Git no Microsoft Fabric

No Microsoft Fabric:
* Os artefatos são serializados em texto legível por humanos:
  * **Relatórios:** Formato `.pbip` com arquivos `visual.json`, `page.json` e `report.json`.
  * **Modelos Semânticos:** Formato TMDL (`.tmdl`) com tabelas, medidas DAX e relacionamentos.
  * **Notebooks:** Formato `.ipynb` ou arquivos de script.
  * **Pipelines:** Definições em JSON da esteira de orquestração.
* Toda alteração feita no workspace gera um status no painel **Controle de código-fonte**.

---

## Passo a Passo: Fazendo um Commit pelo Fabric

### 1. Acessar o Painel de Controle de Código-Fonte
1. No menu lateral esquerdo do Workspace, clique no ícone de branch com o nome **Controle de código-fonte**.
2. O painel lateral abrirá listando a branch atual (ex: `main/fabric`) e o número de itens alterados na aba **Alterações**.

### 2. Selecionar Apenas os Artefatos Desejados
Você tem controle sobre o que vai ou não para o commit.
* Por exemplo, se você alterou apenas uma medida DAX e um gráfico no relatório:
  * Marque `sm_focus_market_intelligence` (Modelo Semântico)
  * Marque `rpt_focus_market_intelligence` (Relatório)
  * Deixe desmarcado itens não modificados ou de infraestrutura (como `wh_focus_intelligence`).

### 3. Escrever uma Mensagem de Commit Profissional
Siga o padrão internacional **Conventional Commits**:
* `feat(report): finalize page 3 interest rates and inflation and update semantic model`
* `fix(dax): correct fisher equation division by zero handling`
* `refactor(dbt): optimize gold layer surrogate keys`

### 4. Confirmar o Commit
1. Cole a mensagem no campo **"Mensagem de Confirmação Opcional"**.
2. Clique no botão **Confirmar**.
3. O Fabric enviará os arquivos serializados diretamente para o GitHub na branch configurada.

---

## Recebendo Alterações do GitHub no Fabric (Sincronização / Atualização)

Quando outro desenvolvedor subir código no GitHub ou quando você fizer push via terminal:
1. No painel de **Controle de código-fonte**, o Fabric exibirá uma notificação na aba **Atualizações**.
2. Clique em **Atualizar tudo**.
3. O Fabric recarregará os artefatos no workspace com o código mais recente do repositório.

---

## Boas Práticas de Governança
* **Commits Atômicos:** Evite commitar tudo de uma vez. Separe commits de modelo semântico (`sm_...`) de commits de relatório (`rpt_...`) quando fizer alterações de grande porte.
* **Nunca commite credenciais:** Parâmetros de conexão e segredos devem residir em Azure Key Vault ou conexões de serviço gerenciadas pelo Fabric.
