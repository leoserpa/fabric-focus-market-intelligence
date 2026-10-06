{{ config(
    materialized = 'table',
    schema = 'gold'
) }}

WITH n1 AS (
    SELECT 0 AS n UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4
    UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9
),
n2 AS (SELECT a.n + b.n * 10 AS n FROM n1 a CROSS JOIN n1 b),
n3 AS (SELECT a.n + b.n * 100 AS n FROM n2 a CROSS JOIN n1 b),
numbers AS (
    SELECT a.n + b.n * 1000 AS n 
    FROM n3 a 
    CROSS JOIN n2 b 
    WHERE a.n + b.n * 1000 <= 20000
),
date_range AS (
    SELECT DATEADD(day, n, CAST('1995-01-01' AS DATE)) AS data
    FROM numbers
    WHERE DATEADD(day, n, CAST('1995-01-01' AS DATE)) <= '2035-12-31'
)

SELECT
    CAST(CONVERT(VARCHAR(8), data, 112) AS INT) AS data_sk,
    data,
    YEAR(data) AS ano,
    MONTH(data) AS mes,
    DAY(data) AS dia,
    DATEPART(quarter, data) AS trimestre,
    CASE WHEN MONTH(data) <= 6 THEN 1 ELSE 2 END AS semestre,
    CAST(DATENAME(month, data) AS VARCHAR(20)) AS nome_mes,
    CAST(CONVERT(VARCHAR(7), data, 120) AS VARCHAR(7)) AS ano_mes,
    DATEPART(weekday, data) AS dia_semana_num,
    CAST(DATENAME(weekday, data) AS VARCHAR(20)) AS dia_semana_nome,
    CASE WHEN DATEPART(weekday, data) IN (1, 7) THEN 0 ELSE 1 END AS flg_dia_util_teorico
FROM date_range
