# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "0e608777-b469-4b47-8d2a-dcc4ba17ffbc",
# META       "default_lakehouse_name": "lk_focus_intelligence",
# META       "default_lakehouse_workspace_id": "217c128f-7b83-4127-989b-4052ea6fff03",
# META       "known_lakehouses": [
# META         {
# META           "id": "0e608777-b469-4b47-8d2a-dcc4ba17ffbc"
# META         }
# META       ]
# META     }
# META   }
# META }

# MARKDOWN ********************

# # Focus Market Intelligence | Bronze to Silver
# 
# ### Curadoria Orientada a Metadados com Quality Gates
# 
# **Projeto:** Focus Market Intelligence Terminal  
# **Plataforma:** Microsoft Fabric (Lakehouse `lh_focus_intelligence`)  
# **Arquitetura:** Medallion | Bronze → Silver  
# **Tecnologia:** PySpark & Delta Lake (OneLake)  
# **Notebook:** `nb_02_bronze_to_silver`
# 
# ### Objetivo
# 
# Transformar as tabelas Bronze em tabelas Silver **tipadas, validadas e deduplicadas**, no mesmo padrão do `nb_01`: um **catálogo declarativo** define cada tabela e uma única função genérica (`curar_silver`) aplica as regras. Cada tabela é isolada: se uma falhar, o erro é registrado em `silver_audit_log`, as demais continuam e o notebook **termina com erro** no final para o Pipeline do Fabric detectar.
# 
# **Principais etapas:**
# 
# - Importação de bibliotecas e ativação de otimizações de escrita do Fabric (V-Order e OptimizeWrite)
# - Definição do catálogo declarativo de curadoria Silver (`CATALOGO_SILVER`)
# - Aplicação de tipagem rigorosa, deduplicação determinística e rastreabilidade de linhagem
# - Quality Gates de integridade de conversão, chaves de negócio e restrições de domínio
# - Execução isolada por tabela com persistência na tabela de auditoria `silver_audit_log`
# - Validação consolidada de execução para orquestração no Fabric Pipeline


# MARKDOWN ********************

# # 0. Imports e Otimizações do Fabric

# CELL ********************

import uuid
from datetime import datetime
from typing import NamedTuple, Optional
from pyspark.sql import DataFrame, functions as F
from pyspark.sql.window import Window

# Otimizações de escrita do Fabric Lakehouse (Skill: fabric-lakehouse)
spark.conf.set("spark.sql.parquet.vorder.enabled", "true")
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")

print(f"Sessão Spark ativa no Microsoft Fabric: {spark.version}")
print("✅ Otimizações V-Order e Delta OptimizeWrite ativadas.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 1. Motor de Curadoria Silver
# 
# - **`Coluna`**: contrato de cada coluna (origem na Bronze → destino na Silver, tipo e formato de data).
# - **`curar_silver`**: aplica, nesta ordem:
#   1. **Contrato de schema:** todas as colunas de origem precisam existir na Bronze.
#   2. **Tipagem** explícita e nomes em `snake_case`.
#   3. **Quality gates** numa única agregação: falhas de conversão por coluna, nulos na chave obrigatória e regras de negócio da tabela.
#   4. **Deduplicação determinística** pela chave natural: mantém o registro mais recente da Bronze e desempata pelas medidas.
#   5. **Gravação Delta** com colunas de linhagem (`_bronze_*`) e auditoria (`_silver_*`).

# CELL ********************

class Coluna(NamedTuple):
    origem: str
    destino: str
    tipo: str
    formato: Optional[str] = None  # usado apenas quando tipo == "date"

def _converter(c: Coluna):
    """Converte a coluna da Bronze para o tipo da Silver."""
    return F.to_date(F.col(c.origem), c.formato) if c.tipo == "date" else F.col(c.origem).cast(c.tipo)

def curar_silver(cfg: dict, batch_id: str) -> dict:
    """Bronze -> Silver: contrato de schema, tipagem, quality gates, deduplicação e gravação Delta."""
    df_bronze = spark.table(cfg["fonte"])
    colunas, chave = cfg["colunas"], cfg["chave"]
    destinos = [c.destino for c in colunas]

    # Gate 1 - Contrato de schema
    faltando = {c.origem for c in colunas} - set(df_bronze.columns)
    if faltando:
        raise ValueError(f"Colunas ausentes em '{cfg['fonte']}': {sorted(faltando)}")

    # Tipagem (mantém o valor bruto em _raw_* apenas para validar a conversão)
    df_tipado = df_bronze.select(
        *[_converter(c).alias(c.destino) for c in colunas],
        *[F.col(c.origem).alias(f"_raw_{c.destino}") for c in colunas],
        F.col("_ingestion_timestamp").alias("_bronze_ingestion_timestamp"),
        F.col("_batch_id").alias("_bronze_batch_id"),
    ).cache()

    try:
        # Gates 2, 3 e 4 numa única passada sobre os dados
        chave_obrigatoria = [k for k in chave if k not in cfg.get("chave_anulavel", [])]
        metricas = df_tipado.agg(
            F.count(F.lit(1)).alias("linhas"),
            *[F.sum((F.col(f"_raw_{d}").isNotNull() & F.col(d).isNull()).cast("int")).alias(f"conversao_falhou__{d}")
              for d in destinos],
            *[F.sum(F.col(k).isNull().cast("int")).alias(f"chave_nula__{k}") for k in chave_obrigatoria],
            *[F.sum(F.when(~F.expr(expr), 1).otherwise(0)).alias(f"regra__{nome}")
              for nome, expr in cfg.get("regras", {}).items()],
        ).first().asDict()

        violacoes = {k: v for k, v in metricas.items() if k != "linhas" and v}
        if violacoes:
            raise ValueError(f"Quality gate reprovado: {violacoes}")

        # Deduplicação determinística: registro mais recente da Bronze; empate desfeito pelas medidas
        medidas = [d for d in destinos if d not in chave]
        janela = Window.partitionBy(*chave).orderBy(
            F.col("_bronze_ingestion_timestamp").desc(), *[F.col(m).desc_nulls_last() for m in medidas])

        df_silver = (df_tipado
                     .withColumn("_rn", F.row_number().over(janela))
                     .filter(F.col("_rn") == 1)
                     .select(*destinos, "_bronze_batch_id", "_bronze_ingestion_timestamp")
                     .withColumn("_silver_batch_id", F.lit(batch_id))
                     .withColumn("_silver_timestamp", F.current_timestamp()))

        (df_silver.write.format("delta").mode("overwrite")
         .option("overwriteSchema", "true").saveAsTable(cfg["destino"]))
    finally:
        df_tipado.unpersist()

    lidos, gravados = metricas["linhas"], spark.table(cfg["destino"]).count()
    print(f"  ✅ {cfg['destino']}: {gravados:,} linhas ({lidos - gravados:,} duplicatas removidas)")
    return {"lidos": lidos, "gravados": gravados, "duplicatas": lidos - gravados}

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 2. Catálogo de Metadados da Camada Silver
# 
# Cada tabela declara: fonte Bronze, destino Silver, contrato de colunas, **chave natural** (deduplicação), colunas da chave que podem ser nulas e **regras de negócio** (expressões SQL que todo registro precisa satisfazer).
# 
# > `indicador_detalhe` é anulável: para IPCA, Selic, Câmbio e PIB Total o BCB não preenche esse campo.

# CELL ********************

ESTATISTICAS_FOCUS = [
    Coluna("Media", "media", "double"),
    Coluna("Mediana", "mediana", "double"),
    Coluna("DesvioPadrao", "desvio_padrao", "double"),
    Coluna("Minimo", "minimo", "double"),
    Coluna("Maximo", "maximo", "double"),
]
REGRA_FAIXA = {"mediana_entre_min_max": "mediana BETWEEN minimo AND maximo"}

CATALOGO_SILVER = [
    {
        "fonte": "bronze_focus_anuais",
        "destino": "silver_focus_anuais",
        "colunas": [
            Coluna("Data", "data", "date", "yyyy-MM-dd"),
            Coluna("Indicador", "indicador", "string"),
            Coluna("IndicadorDetalhe", "indicador_detalhe", "string"),
            Coluna("DataReferencia", "ano_referencia", "int"),
            Coluna("baseCalculo", "base_calculo", "int"),
            *ESTATISTICAS_FOCUS,
            Coluna("numeroRespondentes", "numero_respondentes", "int"),
        ],
        "chave": ["data", "indicador", "indicador_detalhe", "ano_referencia", "base_calculo"],
        "chave_anulavel": ["indicador_detalhe"],
        "regras": REGRA_FAIXA,
    },
    {
        "fonte": "bronze_focus_top5_anuais",
        "destino": "silver_focus_top5_anuais",
        "colunas": [
            Coluna("Data", "data", "date", "yyyy-MM-dd"),
            Coluna("Indicador", "indicador", "string"),
            Coluna("DataReferencia", "ano_referencia", "int"),
            Coluna("tipoCalculo", "tipo_calculo", "string"),
            *ESTATISTICAS_FOCUS,
        ],
        "chave": ["data", "indicador", "ano_referencia", "tipo_calculo"],
        "regras": REGRA_FAIXA,
    },
    {
        "fonte": "bronze_focus_inflacao_12m",
        "destino": "silver_focus_inflacao_12m",
        "colunas": [
            Coluna("Data", "data", "date", "yyyy-MM-dd"),
            Coluna("Indicador", "indicador", "string"),
            Coluna("Suavizada", "suavizada", "string"),
            Coluna("baseCalculo", "base_calculo", "int"),
            *ESTATISTICAS_FOCUS,
            Coluna("numeroRespondentes", "numero_respondentes", "int"),
        ],
        "chave": ["data", "indicador", "suavizada", "base_calculo"],
        "regras": {**REGRA_FAIXA, "somente_suavizada": "suavizada = 'S'"},
    },
    {
        "fonte": "bronze_sgs_selic_meta",
        "destino": "silver_sgs_selic_meta",
        "colunas": [
            Coluna("data", "data", "date", "dd/MM/yyyy"),
            Coluna("valor", "taxa_selic_meta_aa", "double"),
        ],
        "chave": ["data"],
        "regras": {"taxa_preenchida_e_positiva": "taxa_selic_meta_aa IS NOT NULL AND taxa_selic_meta_aa > 0"},
    },
]

print(f"Catálogo Silver carregado com {len(CATALOGO_SILVER)} tabelas.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 3. Execução e Auditoria Persistida
# 
# Cada tabela roda isolada com o mesmo `batch_id`. O resultado de **todas** as tabelas (sucesso ou erro) é gravado em modo **append** em `silver_audit_log`, com o mesmo formato do `bronze_audit_log`.

# CELL ********************

BATCH_ID = str(uuid.uuid4())
resultados_execucao = []

for cfg in CATALOGO_SILVER:
    inicio = datetime.now()
    print(f"Processando: {cfg['fonte']} -> {cfg['destino']}")
    try:
        r, status, erro = curar_silver(cfg, BATCH_ID), "OK", None
    except Exception as e:
        r, status, erro = {"lidos": 0, "gravados": 0, "duplicatas": 0}, "ERRO", f"{type(e).__name__}: {e}"[:1000]
        print(f"  ❌ Falha em '{cfg['destino']}': {erro}")
    fim = datetime.now()
    resultados_execucao.append((BATCH_ID, cfg["destino"], status, r["lidos"], r["gravados"], r["duplicatas"],
                                erro, inicio, fim, round((fim - inicio).total_seconds(), 1)))

SCHEMA_AUDITORIA = ("batch_id string, tabela string, status string, registros_lidos long, registros_gravados long, "
                    "duplicatas_removidas long, erro string, inicio timestamp, fim timestamp, duracao_s double")
df_auditoria = spark.createDataFrame(resultados_execucao, SCHEMA_AUDITORIA)
(df_auditoria.write.format("delta").mode("append")
 .option("mergeSchema", "true").saveAsTable("silver_audit_log"))

print(f"\n📝 Auditoria do batch {BATCH_ID} gravada em 'silver_audit_log'.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 4. Validação e Sinalização de Falha
# 
# Se alguma tabela falhou, o notebook é **encerrado com erro** para o Pipeline do Fabric marcar a execução como falha.

# CELL ********************

display(df_auditoria)

falhas = df_auditoria.filter(F.col("status") != "OK").select("tabela", "erro").collect()
if falhas:
    raise RuntimeError(f"{len(falhas)} tabela(s) falharam na Silver: " +
                       "; ".join(f"{f.tabela} -> {f.erro}" for f in falhas))

print("🎉 Camada Silver processada e validada com sucesso!")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 5. Conclusões
# 
# - Catálogo declarativo + função única, no mesmo padrão do `nb_01`
# - Contrato de schema, gate de conversão, chave obrigatória e regras de negócio antes de gravar
# - Deduplicação determinística pela chave natural
# - Linhagem Bronze → Silver preservada (`_bronze_batch_id`, `_bronze_ingestion_timestamp`)
# - Auditoria de sucesso **e falha** em `silver_audit_log`, com falha explícita para o Pipeline
# - V-Order + OptimizeWrite para leitura rápida no Direct Lake
# 
# Próximo passo: **`nb_03_silver_to_gold`**.
