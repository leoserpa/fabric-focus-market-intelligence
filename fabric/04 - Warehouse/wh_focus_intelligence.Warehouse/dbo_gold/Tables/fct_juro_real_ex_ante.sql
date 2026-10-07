CREATE TABLE [dbo_gold].[fct_juro_real_ex_ante] (
    [data_sk]                INT        NULL,
    [data]                   DATE       NULL,
    [taxa_selic_meta_aa]     FLOAT (53) NULL,
    [ipca_esperado_12m]      FLOAT (53) NULL,
    [desvio_padrao_ipca_12m] FLOAT (53) NULL,
    [taxa_juro_real_ex_ante] FLOAT (53) NULL
);


GO