CREATE TABLE [dbo_gold].[fct_comparativo_top5] (
    [data_sk]                  INT            NULL,
    [data]                     DATE           NULL,
    [indicador]                VARCHAR (8000) NULL,
    [ano_referencia]           INT            NULL,
    [mediana_mercado]          FLOAT (53)     NULL,
    [mediana_top5]             FLOAT (53)     NULL,
    [divergencia_top5_mercado] FLOAT (53)     NULL,
    [desvio_padrao_mercado]    FLOAT (53)     NULL,
    [desvio_padrao_top5]       FLOAT (53)     NULL,
    [minimo_mercado]           FLOAT (53)     NULL,
    [maximo_mercado]           FLOAT (53)     NULL,
    [minimo_top5]              FLOAT (53)     NULL,
    [maximo_top5]              FLOAT (53)     NULL,
    [numero_respondentes]      INT            NULL,
    [sinal_posicionamento]     VARCHAR (40)   NULL
);


GO