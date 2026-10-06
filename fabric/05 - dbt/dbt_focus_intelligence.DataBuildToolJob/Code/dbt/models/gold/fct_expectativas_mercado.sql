{{ config(
    materialized = 'table',
    schema = 'gold'
) }}

WITH silver_anuais AS (
    SELECT * FROM {{ source('lakehouse_silver', 'silver_focus_anuais') }}
)

SELECT
    CAST(CONVERT(VARCHAR(8), data, 112) AS INT) AS data_sk,
    data,
    indicador,
    CAST(COALESCE(indicador_detalhe, 'Geral') AS VARCHAR(50)) AS indicador_detalhe,
    ano_referencia,
    base_calculo,
    CAST(
        CASE 
            WHEN base_calculo = 0 THEN '30 dias corridos'
            WHEN base_calculo = 1 THEN '5 dias úteis'
            ELSE 'Outro'
        END AS VARCHAR(30)
    ) AS base_calculo_desc,
    media,
    mediana,
    desvio_padrao,
    minimo,
    maximo,
    ROUND(maximo - minimo, 4) AS spread_min_max,
    numero_respondentes
FROM silver_anuais
