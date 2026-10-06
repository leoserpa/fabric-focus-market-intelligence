{{ config(
    materialized = 'table',
    schema = 'gold'
) }}

WITH selic_meta AS (
    SELECT
        data,
        taxa_selic_meta_aa
    FROM {{ source('lakehouse_silver', 'silver_sgs_selic_meta') }}
),

inflacao_12m AS (
    SELECT
        data,
        mediana AS ipca_esperado_12m,
        media AS ipca_media_12m,
        desvio_padrao AS desvio_padrao_ipca_12m
    FROM {{ source('lakehouse_silver', 'silver_focus_inflacao_12m') }}
    WHERE base_calculo = 1 -- Base mais atualizada de 5 dias úteis
)

SELECT
    CAST(CONVERT(VARCHAR(8), s.data, 112) AS INT) AS data_sk,
    s.data,
    s.taxa_selic_meta_aa,
    i.ipca_esperado_12m,
    i.desvio_padrao_ipca_12m,
    -- Equação de Fisher: ((1 + Selic/100) / (1 + IPCA_12m/100) - 1) * 100
    ROUND(
        (
            ( (1.0 + (s.taxa_selic_meta_aa / 100.0)) / (1.0 + (i.ipca_esperado_12m / 100.0)) ) - 1.0
        ) * 100.0,
        4
    ) AS taxa_juro_real_ex_ante
FROM selic_meta s
INNER JOIN inflacao_12m i
    ON s.data = i.data
