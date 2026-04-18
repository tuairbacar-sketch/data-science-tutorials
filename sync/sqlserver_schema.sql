CREATE TABLE staging_raw (
    id BIGINT NOT NULL,
    payload NVARCHAR(MAX) NOT NULL,
    hash_payload CHAR(64) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT GETDATE()
);
GO

CREATE INDEX IX_staging_hash ON staging_raw(hash_payload);
GO

CREATE TABLE sync_log (
    id INT IDENTITY(1,1) PRIMARY KEY,
    status VARCHAR(20) NOT NULL,
    origem_dados VARCHAR(20) NOT NULL,
    total_linhas INT NOT NULL,
    erro_msg NVARCHAR(MAX) NULL,
    data_execucao DATETIME NOT NULL DEFAULT GETDATE(),
    CONSTRAINT CK_sync_log_status CHECK (status IN ('SUCESSO', 'ERRO'))
);
GO

-- Pré-requisito: a tabela dbo.tabela_producao deve existir antes de criar/executar a procedure.
CREATE OR ALTER PROCEDURE dbo.MergeStagingToProducao
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @merge_actions TABLE (action_name NVARCHAR(10));

    MERGE dbo.tabela_producao AS T
    USING staging_raw AS S
    ON T.id = S.id
    WHEN MATCHED AND T.hash_payload <> S.hash_payload THEN
        UPDATE SET
            T.payload = S.payload,
            T.hash_payload = S.hash_payload,
            T.updated_at = GETDATE()
    WHEN NOT MATCHED THEN
        INSERT (id, payload, hash_payload)
        VALUES (S.id, S.payload, S.hash_payload)
    OUTPUT $action INTO @merge_actions(action_name);

    SELECT COUNT(1) AS linhas_afetadas
    FROM @merge_actions;
END
GO
