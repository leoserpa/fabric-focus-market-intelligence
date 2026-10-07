CREATE TABLE [dbo_gold].[dim_indicador] (
    [indicador_id]   INT          NOT NULL,
    [indicador]      VARCHAR (18) NOT NULL,
    [unidade_medida] VARCHAR (6)  NOT NULL,
    [periodicidade]  VARCHAR (8)  NOT NULL,
    [descricao]      VARCHAR (98) NOT NULL
);


GO