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

# # Focus Market Intelligence | Raw to Bronze
# 
# ### Ingestão Orientada a Metadados das Expectativas do Boletim Focus e Indicadores do BCB
# 
# **Projeto:** Focus Market Intelligence Terminal  
# **Plataforma:** Microsoft Fabric  
# **Arquitetura:** Medallion | Raw → Bronze (Metadata-Driven Framework com Quality Gates)  
# **Tecnologia:** PySpark, Delta Lake (OneLake) & Requests/Urllib3  
# **Notebook:** `nb_01_raw_to_bronze`
# 
# ### Objetivo
# 
# Implementar um pipeline de ingestão automatizado, resiliente e orientado a metadados para consumir **todo o histórico** dos serviços de dados abertos do Banco Central do Brasil (BCB).
# 
# Cada tipo de fonte possui um **extrator gerador** enxuto (paginação OData com ordenação determinística e janelas de 5 anos no SGS). Antes de qualquer gravação, a carga passa por **quality gates** (atualização, volume e schema): se algum falhar, a tabela Bronze anterior é preservada. Cada execução é registrada na tabela **`bronze_audit_log`**, e o notebook **termina com erro** quando alguma fonte falha, para que o Pipeline do Fabric detecte o problema.
# 
# **Principais etapas:**
# 
# - Importação das bibliotecas e ativação das otimizações do Fabric (V-Order e Optimize Write)
# - Sessão HTTP resiliente, extratores por fonte e quality gates
# - Definição do catálogo declarativo de fontes (Metadata Catalog)
# - Execução em lote com isolamento de falhas e auditoria persistida
# - Validação da carga e sinalização de falha para o Pipeline
# - Conclusões e preparação dos dados para a camada Silver


# MARKDOWN ********************

# # 0. Instalando e Importando Bibliotecas Necessárias

# CELL ********************

# Imports Globais
import json
import uuid
import requests
from datetime import datetime, date, timedelta
from urllib.parse import urlencode, quote
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
from pyspark.sql import functions as F

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

# # 1. Sessão HTTP, Extratores e Quality Gates
# 
# - **`_get_json`**: único ponto de requisição HTTP, com retry exponencial (429/5xx) e **fail-fast** para respostas vazias.
# - **`extrair_odata`**: pagina a API Olinda via `$top`/`$skip`, **ordenando pela chave natural completa** da fonte. Sem isso, linhas com a mesma `Data` podem mudar de posição entre páginas e ser duplicadas ou perdidas.
# - **`extrair_sgs`**: percorre a série SGS em janelas de 5 anos (a API rejeita janelas acima de 10 anos em séries diárias).
# - **`validar_qualidade`**: quality gates executados **antes** do overwrite:
#   - **Atualização:** a data mais recente não pode estar atrasada além do limite da fonte.
#   - **Volume:** a carga nova não pode ter menos de 90% das linhas da tabela atual.
#   - **Schema:** nenhuma coluna existente pode desaparecer da origem.
#   - **Unicidade:** duplicatas pela chave natural geram alerta (tratadas na Silver).
# - **`ingerir_bronze`**: orquestra extração, validação, colunas de auditoria e gravação Delta.


# CELL ********************

OLINDA_BASE = "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata"
SGS_BASE = "https://api.bcb.gov.br/dados/serie/bcdata.sgs"
LIMITE_QUEDA_VOLUME = 0.90  # bloqueia a carga se vier com menos de 90% das linhas atuais

# Sessão HTTP com retry exponencial para instabilidades e rate-limit do BCB
http = requests.Session()
http.mount("https://", HTTPAdapter(max_retries=Retry(
    total=5, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])))
http.headers.update({"User-Agent": "FabricTradingTerminal/1.0", "Accept": "application/json"})

def _get_json(url: str):
    """GET único com fail-fast: erro HTTP ou corpo vazio interrompem a carga da fonte."""
    resp = http.get(url, timeout=120)
    resp.raise_for_status()
    if not resp.text.strip():
        raise ValueError(f"Resposta vazia do BCB: {url}")
    return resp.json()

def extrair_odata(cfg: dict):
    """Pagina a API Olinda via $top/$skip com ordenação determinística pela chave natural."""
    tamanho, skip = cfg.get("page_size", 15000), 0
    while True:
        params = {"$format": "json", "$top": tamanho, "$skip": skip,
                  "$orderby": ",".join(cfg["chave"]), "$filter": cfg["filtro"]}
        lote = _get_json(f"{OLINDA_BASE}/{cfg['endpoint']}?{urlencode(params, quote_via=quote)}")["value"]
        yield from lote
        if len(lote) < tamanho:
            break
        skip += tamanho

def extrair_sgs(cfg: dict):
    """Percorre a série SGS em janelas de 5 anos (limite da API: 10 anos para séries diárias)."""
    ini, hoje = datetime.strptime(cfg["data_inicial"], "%d/%m/%Y").date(), date.today()
    while ini <= hoje:
        fim = min(ini + timedelta(days=5 * 365), hoje)
        yield from _get_json(f"{SGS_BASE}.{cfg['codigo_sgs']}/dados?formato=json"
                             f"&dataInicial={ini:%d/%m/%Y}&dataFinal={fim:%d/%m/%Y}")
        ini = fim + timedelta(days=1)

EXTRATORES = {"ODATA": extrair_odata, "SGS": extrair_sgs}

def validar_qualidade(cfg: dict, registros: list) -> date:
    """Quality gates executados ANTES do overwrite. Qualquer violação bloqueia a gravação."""
    tabela = cfg["tabela_destino"]

    # Gate 1 - Atualização: a fonte precisa trazer dados recentes
    data_max = max(datetime.strptime(r[cfg["coluna_data"]], cfg["formato_data"]).date() for r in registros)
    atraso = (date.today() - data_max).days
    if atraso > cfg["max_dias_atraso"]:
        raise ValueError(f"Dado desatualizado: última data {data_max} ({atraso} dias de atraso)")

    # Alerta - Unicidade pela chave natural (duplicatas são tratadas na Silver)
    if cfg.get("chave"):
        duplicatas = len(registros) - len({tuple(r.get(k) for k in cfg["chave"]) for r in registros})
        if duplicatas:
            print(f"  ⚠️ {duplicatas:,} registros duplicados pela chave {cfg['chave']}")

    if not spark.catalog.tableExists(tabela):
        return data_max  # primeira carga: sem base de comparação
    atual = spark.table(tabela)

    # Gate 2 - Volume: protege contra respostas parciais da API
    qtd_atual = atual.count()
    if len(registros) < qtd_atual * LIMITE_QUEDA_VOLUME:
        raise ValueError(f"Queda de volume: {len(registros):,} linhas novas vs {qtd_atual:,} atuais")

    # Gate 3 - Schema: nenhuma coluna de negócio pode sumir da origem
    colunas_novas = set().union(*(r.keys() for r in registros))
    faltando = {c for c in atual.columns if not c.startswith("_")} - colunas_novas
    if faltando:
        raise ValueError(f"Colunas ausentes na origem: {sorted(faltando)}")

    return data_max

def ingerir_bronze(cfg: dict, batch_id: str) -> dict:
    """Extrai a fonte inteira, valida, adiciona colunas de auditoria e grava em Delta."""
    tabela = cfg["tabela_destino"]
    print(f"Iniciando ingestão: [{cfg['descricao']}] -> {tabela}")

    registros = list(EXTRATORES[cfg["tipo_fonte"]](cfg))
    if not registros:
        raise ValueError("Nenhum registro retornado pela fonte")

    data_max = validar_qualidade(cfg, registros)

    # spark.read.json evita CANNOT_DETERMINE_TYPE em colunas 100% nulas
    df = (spark.read.json(spark.sparkContext.parallelize([json.dumps(r) for r in registros]))
          .withColumn("_batch_id", F.lit(batch_id))
          .withColumn("_ingestion_timestamp", F.current_timestamp())
          .withColumn("_source_url", F.lit(cfg.get("endpoint") or f"sgs.{cfg.get('codigo_sgs')}")))

    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(tabela)

    print(f"  ✅ {len(registros):,} linhas gravadas em '{tabela}' ({len(df.columns)} colunas, última data {data_max}).\n")
    return {"registros": len(registros), "colunas": len(df.columns), "data_max": data_max}

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 2. Catálogo de Metadados das Fontes (Metadata Catalog)
# 
# Definição centralizada e declarativa das fontes do Banco Central, sem corte temporal. Além da origem, cada fonte declara sua **chave natural** (usada na ordenação da paginação e no alerta de unicidade) e seus **parâmetros de atualização** (coluna de data, formato e atraso máximo tolerado).

# CELL ********************

# Catálogo Central de Configuração da Camada Bronze (Histórico Completo)
CATALOGO_BRONZE = [
    {
        "descricao": "Focus Anual - Consenso Geral (IPCA, Selic, Câmbio, PIB)",
        "tipo_fonte": "ODATA",
        "endpoint": "ExpectativasMercadoAnuais",
        "filtro": "Indicador eq 'IPCA' or Indicador eq 'Selic' or Indicador eq 'Câmbio' or Indicador eq 'PIB Total'",
        "chave": ["Data", "Indicador", "IndicadorDetalhe", "DataReferencia", "baseCalculo"],
        "coluna_data": "Data", "formato_data": "%Y-%m-%d", "max_dias_atraso": 10,
        "tabela_destino": "bronze_focus_anuais"
    },
    {
        "descricao": "Focus Anual - Grupo Top 5 (Instituições de Maior Assertividade)",
        "tipo_fonte": "ODATA",
        "endpoint": "ExpectativasMercadoTop5Anuais",
        "filtro": "tipoCalculo eq 'C' and (Indicador eq 'IPCA' or Indicador eq 'Selic' or Indicador eq 'Câmbio')",
        "chave": ["Data", "Indicador", "DataReferencia", "tipoCalculo"],
        "coluna_data": "Data", "formato_data": "%Y-%m-%d", "max_dias_atraso": 10,
        "tabela_destino": "bronze_focus_top5_anuais"
    },
    {
        "descricao": "Focus - Inflação Esperada 12M Suavizada (Juro Real)",
        "tipo_fonte": "ODATA",
        "endpoint": "ExpectativasMercadoInflacao12Meses",
        "filtro": "Indicador eq 'IPCA' and Suavizada eq 'S'",
        "chave": ["Data", "Indicador", "Suavizada", "baseCalculo"],
        "coluna_data": "Data", "formato_data": "%Y-%m-%d", "max_dias_atraso": 10,
        "tabela_destino": "bronze_focus_inflacao_12m"
    },
    {
        "descricao": "SGS 432 - Taxa Selic Meta Diária (desde o início da série)",
        "tipo_fonte": "SGS",
        "codigo_sgs": 432,
        "data_inicial": "04/06/1999",
        "chave": ["data"],
        "coluna_data": "data", "formato_data": "%d/%m/%Y", "max_dias_atraso": 5,
        "tabela_destino": "bronze_sgs_selic_meta"
    }
]

print(f"Catálogo carregado com {len(CATALOGO_BRONZE)} fontes configuradas para ingestão.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 3. Execução do Pipeline Bronze e Auditoria Persistida
# 
# Execução sequencial do catálogo com um `batch_id` único por execução. Cada fonte é isolada: se uma falhar, o erro é registrado e as demais continuam. Ao final, o resultado de todas as fontes é gravado em modo **append** na tabela Delta **`bronze_audit_log`**, formando o histórico de execuções para monitoramento.

# CELL ********************

BATCH_ID = str(uuid.uuid4())
resultados_execucao = []

for cfg in CATALOGO_BRONZE:
    inicio = datetime.now()
    try:
        r, status, erro = ingerir_bronze(cfg, BATCH_ID), "OK", None
    except Exception as e:
        r, status, erro = {"registros": 0, "colunas": 0, "data_max": None}, "ERRO", f"{type(e).__name__}: {e}"[:1000]
        print(f"  ❌ Falha em '{cfg['tabela_destino']}': {erro}\n")
    fim = datetime.now()
    resultados_execucao.append((BATCH_ID, cfg["tabela_destino"], status, r["registros"], r["colunas"],
                                r["data_max"], erro, inicio, fim, round((fim - inicio).total_seconds(), 1)))

# Auditoria persistida (append) para histórico e monitoramento
SCHEMA_AUDITORIA = ("batch_id string, tabela string, status string, registros long, colunas int, "
                    "data_max date, erro string, inicio timestamp, fim timestamp, duracao_s double")
df_auditoria = spark.createDataFrame(resultados_execucao, SCHEMA_AUDITORIA)
df_auditoria.write.format("delta").mode("append").saveAsTable("bronze_audit_log")

print(f"📝 Auditoria do batch {BATCH_ID} gravada em 'bronze_audit_log'.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 4. Validação da Camada Bronze
# 
# Exibição da auditoria desta execução. Se alguma fonte falhou, o notebook é **encerrado com erro**, para que o Pipeline do Fabric (Passo 5) marque a execução como falha em vez de sucesso.

# CELL ********************

display(df_auditoria)

falhas = df_auditoria.filter(F.col("status") != "OK").select("tabela", "erro").collect()
if falhas:
    raise RuntimeError(f"{len(falhas)} fonte(s) falharam na carga Bronze: " +
                       "; ".join(f"{f.tabela} -> {f.erro}" for f in falhas))

print("🎉 Todas as fontes carregadas e validadas com sucesso!")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 5. Conclusões
# 
# A ingestão da camada Raw para a camada Bronze foi concluída com o framework de metadados, quality gates e auditoria persistida.
# 
# ### Principais resultados
# 
# - Sessão HTTP com retry exponencial contra instabilidades e rate-limit do BCB
# - Paginação OData com ordenação determinística pela chave natural (sem perda ou duplicação entre páginas)
# - Janelas de 5 anos na API SGS para cobrir todo o histórico da Selic desde 1999
# - Quality gates de atualização, volume e schema executados antes de cada overwrite
# - Auditoria de cada execução persistida na tabela `bronze_audit_log`
# - Falha explícita do notebook quando alguma fonte não é carregada, para o Pipeline do Fabric
# - Otimizações V-Order e Delta OptimizeWrite ativadas para o Direct Lake
# - Carga das 4 tabelas Delta Bronze (`bronze_focus_anuais`, `bronze_focus_top5_anuais`, `bronze_focus_inflacao_12m`, `bronze_sgs_selic_meta`)
# 
# A camada Bronze está consolidada e pronta para o próximo notebook: **`nb_02_bronze_to_silver`**.

