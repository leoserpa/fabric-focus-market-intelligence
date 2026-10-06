{{ config(
    materialized = 'table',
    schema = 'gold'
) }}

WITH consenso AS (
    SELECT
        data,
        indicador,
        ano_referencia,
        base_calculo,
        mediana AS mediana_mercado,
        media AS media_mercado,
        desvio_padrao AS desvio_padrao_mercado,
        minimo AS minimo_mercado,
        maximo AS maximo_mercado,
        numero_respondentes
    FROM {{ source('lakehouse_silver', 'silver_focus_anuais') }}
    WHERE base_calculo = 1 -- Base mais recente de 5 dias úteis
),

top5 AS (
    SELECT
        data,
        indicador,
        ano_referencia,
        tipo_calculo,
        mediana AS mediana_top5,
        media AS media_top5,
        desvio_padrao AS desvio_padrao_top5,
        minimo AS minimo_top5,
        maximo AS maximo_top5
    FROM {{ source('lakehouse_silver', 'silver_focus_top5_anuais') }}
    WHERE tipo_calculo = 'C' -- Ranking de Curto Prazo
)

SELECT
    CAST(CONVERT(VARCHAR(8), c.data, 112) AS INT) AS data_sk,
    c.data,
    c.indicador,
    c.ano_referencia,
    c.mediana_mercado,
    t.mediana_top5,
    ROUND(t.mediana_top5 - c.mediana_mercado, 4) AS divergencia_top5_mercado,
    c.desvio_padrao_mercado,
    t.desvio_padrao_top5,
    c.minimo_mercado,
    c.maximo_mercado,
    t.minimo_top5,
    t.maximo_top5,
    c.numero_respondentes,
    CAST(
        CASE 
            WHEN t.mediana_top5 > c.mediana_mercado THEN 'Top 5 mais alto (Hawkish)'
            WHEN t.mediana_top5 < c.mediana_mercado THEN 'Top 5 mais baixo (Dovish)'
            ELSE 'Em Consenso'
        END AS VARCHAR(40)
    ) AS sinal_posicionamento
FROM consenso c
INNER JOIN top5 t
    ON c.data = t.data
   AND c.indicador = t.indicador
   AND c.ano_referencia = t.ano_referencia
