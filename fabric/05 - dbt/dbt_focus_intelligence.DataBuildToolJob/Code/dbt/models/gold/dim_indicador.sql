{{ config(
    materialized = 'table',
    schema = 'gold'
) }}

SELECT
    indicador_id,
    indicador,
    unidade_medida,
    periodicidade,
    descricao
FROM (
    VALUES
        (1, 'IPCA', '% a.a.', 'Anual', 'Índice Nacional de Preços ao Consumidor Amplo - Medida oficial de inflação calculada pelo IBGE'),
        (2, 'Selic', '% a.a.', 'Anual', 'Taxa Básica de Juros da economia fixada pelo COPOM (fim de período)'),
        (3, 'Câmbio', 'R$/US$', 'Anual', 'Taxa de câmbio comercial de compra e venda do Dólar americano (fim de período)'),
        (4, 'PIB Total', '% a.a.', 'Anual', 'Taxa de crescimento real do Produto Interno Bruto brasileiro'),
        (5, 'IPCA 12M Suavizado', '% a.a.', '12 Meses', 'Expectativa de inflação acumulada para os próximos 12 meses contínuos')
) AS v(indicador_id, indicador, unidade_medida, periodicidade, descricao)
