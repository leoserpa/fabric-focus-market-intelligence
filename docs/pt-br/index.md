# Documentação Técnica - Focus Market Intelligence

Bem-vindo à documentação técnica do projeto **Focus Market Intelligence**, uma plataforma analítica desenvolvida no **Microsoft Fabric**, **dbt** e **Power BI**, dedicada ao monitoramento e análise das expectativas macroeconômicas do Banco Central do Brasil (BCB).

Esta documentação segue a estrutura do framework **[Diátaxis](https://diataxis.fr/)**, dividindo o conhecimento técnico em quatro quadrantes:

---

## Os 4 Quadrantes Diátaxis

```
                     PRÁTICA (Ação)
                           ▲
                           │
        TUTORIAIS          │        HOW-TO GUIDES
   Aprender fazendo        │    Resolver problemas
   (Passo a passo inicial) │    (Receitas específicas)
                           │
APRENDIZADO ───────────────┼─────────────── TRABALHO
(Para iniciantes)          │                (Para o dia a dia)
                           │
        EXPLANATION        │          REFERENCE
      Entender conceitos   │     Consultar especificações
    (Arquitetura e Teoria) │     (Tabelas, DAX e APIs)
                           │
                           ▼
                    TEORIA (Conhecimento)
```

---

### 1. [Tutoriais (Tutorials)](./tutorials/getting-started.md)
Orientado ao aprendizado. Passos práticos para guiar um novo desenvolvedor desde a clonagem do repositório até a execução funcional.
* **[Guia de Inicialização (Getting Started)](./tutorials/getting-started.md)**: Pré-requisitos, configuração de capacidade no Microsoft Fabric, importação de artefatos e primeira execução da esteira.

---

### 2. [Guias Práticos (How-to Guides)](./how-to-guides/run-dbt-pipeline.md)
Orientado a tarefas e soluções de problemas operacionais do dia a dia.
* **[Como Executar e Testar Modelos dbt](./how-to-guides/run-dbt-pipeline.md)**: Passos para rodar transformações com `dbt run`, compilar o DAG e validar testes de qualidade com `dbt test`.
* **[Como Sincronizar o Fabric com o GitHub](./how-to-guides/fabric-git-sync.md)**: Configuração de controle de código-fonte no Microsoft Fabric, branches e fluxo de commit.

---

### 3. [Referência Técnica (Reference)](./reference/data-dictionary.md)
Orientado à informação exata e consulta rápida. Catálogos, contratos de dados e especificações formais.
* **[Dicionário de Dados e Schemas](./reference/data-dictionary.md)**: Mapeamento de tabelas nas camadas Lakehouse (Bronze/Silver), Warehouse (Gold) e chaves de relacionamento.
* **[Catálogo de Medidas DAX](./reference/dax-measures.md)**: Documentação completa das fórmulas DAX do modelo semântico (`sm_focus_market_intelligence`), incluindo a Equação de Fisher, divergências Top 5 e regras de formatação.

---

### 4. [Explicações Conceituais (Explanation)](./explanation/architecture.md)
Orientado ao entendimento aprofundado, decisões de design e teoria econômica.
* **[Arquitetura de Dados no Microsoft Fabric](./explanation/architecture.md)**: Decisões técnicas da arquitetura Medallion, o papel do dbt com Fabric Warehouse e Direct Lake no Power BI.
* **[Metodologia Focus e Equação de Fisher](./explanation/fisher-equation-methodology.md)**: Como o Banco Central coleta e apura as expectativas (Base 1 e Base 0) e a dedução matemática da taxa de juro real ex-ante.

---

## Estrutura do Repositório

```text
focus-market-intelligence/
├── README.md                      # Vitrine executiva do projeto no GitHub
├── docs/                          # Documentação oficial (Diátaxis)
│   ├── index.md                   # Este índice geral
│   ├── tutorials/                 # Tutoriais passo a passo
│   ├── how-to-guides/             # Guias operacionais e receitas
│   ├── reference/                 # Dicionários de dados e medidas DAX
│   └── explanation/               # Decisões arquiteturais e metodologia econômica
└── fabric/                        # Artefatos sincronizados com o Microsoft Fabric
    ├── 01 - Lakehouse/            # lk_focus_intelligence (Delta Tables)
    ├── 02 - Notebooks/            # PySpark: Ingestão e Padronização
    ├── 03 - Pipelines/            # Data Pipeline de orquestração diária
    ├── 04 - Warehouse/            # wh_focus_intelligence (Gold Serving)
    ├── 05 - dbt/                  # dbt_focus_intelligence (Modelagem Dimensional)
    ├── 06 - Semantic Models/      # sm_focus_market_intelligence (TMDL / DAX)
    └── 07 - Reports/              # rpt_focus_market_intelligence (Power BI PBIP)
```
