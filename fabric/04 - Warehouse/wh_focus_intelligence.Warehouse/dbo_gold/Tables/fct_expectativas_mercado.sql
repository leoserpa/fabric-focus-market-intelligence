CREATE TABLE [dbo_gold].[fct_expectativas_mercado] (
    [data_sk]             INT            NULL,
    [data]                DATE           NULL,
    [indicador]           VARCHAR (8000) NULL,
    [indicador_detalhe]   VARCHAR (50)   NULL,
    [ano_referencia]      INT            NULL,
    [base_calculo]        INT            NULL,
    [base_calculo_desc]   VARCHAR (30)   NULL,
    [media]               FLOAT (53)     NULL,
    [mediana]             FLOAT (53)     NULL,
    [desvio_padrao]       FLOAT (53)     NULL,
    [minimo]              FLOAT (53)     NULL,
    [maximo]              FLOAT (53)     NULL,
    [spread_min_max]      FLOAT (53)     NULL,
    [numero_respondentes] INT            NULL
);


GO