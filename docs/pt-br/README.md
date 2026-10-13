# Documentação Técnica - Focus Market Intelligence

Bem-vindo à documentação técnica do projeto **Focus Market Intelligence**, uma plataforma analítica desenvolvida no **Microsoft Fabric**, **dbt** e **Power BI**, dedicada ao monitoramento e análise das expectativas macroeconômicas do Banco Central do Brasil (BCB).

Esta documentação segue a estrutura do framework **[Diátaxis](https://diataxis.fr/)**, dividindo o conhecimento técnico em quatro quadrantes:

---

## Os 4 Quadrantes Diátaxis

```
                     PRÁTICA (Ação)
                           ▲
                           │
        TUTORIAIS          │        GUIAS PRÁTICOS
   Aprender fazendo        │      Resolver problemas
(Passo a passo inicial)    │    (Receitas específicas)
                           │
APRENDIZADO ───────────────┼─────────────── TRABALHO
(Para iniciantes)          │                (Para o dia a dia)
                           │
        EXPLICAÇÃO         │          REFERÊNCIA
    Entender conceitos     │   Consultar especificações
  (Arquitetura e Teoria)   │     (Tabelas, DAX e APIs)
                           │
                           ▼
                    TEORIA (Conhecimento)
```

---

### 1. [Tutoriais](./tutoriais/primeiros-passos.md)
Orientado ao aprendizado. Passos práticos para guiar um novo desenvolvedor desde a clonagem do repositório até a execução funcional.
* **[Guia de Inicialização](./tutoriais/primeiros-passos.md)**: Pré-requisitos, configuração de capacidade no Microsoft Fabric, importação de artefatos e primeira execução da esteira.

---

### 2. [Guias Práticos](./guias-praticos/executar-pipeline-dbt.md)
Orientado a tarefas e soluções de problemas operacionais do dia a dia.
* **[Como Executar e Testar Modelos dbt](./guias-praticos/executar-pipeline-dbt.md)**: Passos para rodar transformações com `dbt run`, compilar o DAG e validar testes de qualidade com `dbt test`.
* **[Como Sincronizar o Fabric com o GitHub](./guias-praticos/sincronizacao-git-fabric.md)**: Configuração de controle de código-fonte no Microsoft Fabric, branches e fluxo de commit.

---

### 3. [Referência Técnica](./referencia/dicionario-de-dados.md)
Orientado à informação exata e consulta rápida. Catálogos, contratos de dados e especificações formais.
* **[Dicionário de Dados e Schemas](./referencia/dicionario-de-dados.md)**: Mapeamento de tabelas nas camadas Lakehouse (Bronze/Silver), Warehouse (Gold) e chaves de relacionamento.
* **[Catálogo de Medidas DAX](./referencia/catalogo-medidas-dax.md)**: Documentação completa das fórmulas DAX do modelo semântico (`sm_focus_market_intelligence`), incluindo a Equação de Fisher, divergências Top 5 e regras de formatação.

---

### 4. [Explicações Conceituais](./explicacao/arquitetura-fabric.md)
Orientado ao entendimento aprofundado, decisões de design e teoria econômica.
* **[Arquitetura de Dados no Microsoft Fabric](./explicacao/arquitetura-fabric.md)**: Decisões técnicas da arquitetura Medallion, o papel do dbt com Fabric Warehouse e Direct Lake no Power BI.
* **[Metodologia Focus e Equação de Fisher](./explicacao/metodologia-focus-e-fisher.md)**: Como o Banco Central coleta e apura as expectativas (Base 1 e Base 0) e a dedução matemática da taxa de juro real ex-ante.

---

## Estrutura do Repositório

```text
focus-market-intelligence/
├── README.md                      # Vitrine executiva em Português
├── README.en.md                   # Vitrine executiva em Inglês
├── docs/                          # Documentação técnica oficial (Diátaxis)
│   ├── README.md                  # Hub de seleção de idiomas
│   ├── pt-br/                     # Documentação em Português
│   │   ├── README.md              # Este índice geral
│   │   ├── tutoriais/             # Tutoriais passo a passo
│   │   ├── guias-praticos/        # Guias operacionais e receitas
│   │   ├── referencia/            # Dicionários de dados e medidas DAX
│   │   └── explicacao/            # Decisões arquiteturais e metodologia econômica
│   └── en/                        # English documentation suite
└── fabric/                        # Artefatos sincronizados com o Microsoft Fabric
    ├── 01 - Lakehouse/            # lk_focus_intelligence (Delta Tables)
    ├── 02 - Notebooks/            # PySpark: Ingestão e Padronização
    ├── 03 - Pipelines/            # Data Pipeline de orquestração diária
    ├── 04 - Warehouse/            # wh_focus_intelligence (Gold Serving)
    ├── 05 - dbt/                  # dbt_focus_intelligence (Modelagem Dimensional)
    ├── 06 - Semantic Models/      # sm_focus_market_intelligence (TMDL / DAX)
    └── 07 - Reports/              # rpt_focus_market_intelligence (Power BI PBIP)
```
