CREATE TABLE [dbo_gold].[dim_calendario] (
    [data_sk]              INT          NULL,
    [data]                 DATE         NULL,
    [ano]                  INT          NULL,
    [mes]                  INT          NULL,
    [dia]                  INT          NULL,
    [trimestre]            INT          NULL,
    [semestre]             INT          NOT NULL,
    [nome_mes]             VARCHAR (20) NULL,
    [ano_mes]              VARCHAR (7)  NULL,
    [dia_semana_num]       INT          NULL,
    [dia_semana_nome]      VARCHAR (20) NULL,
    [flg_dia_util_teorico] INT          NOT NULL
);


GO