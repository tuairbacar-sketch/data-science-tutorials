# ETL Python + Pandas + SQL Server

Fluxo implementado: **API → DataFrame → validação → staging (`fast_executemany`) → MERGE**.

## Arquivos

- `etl.py`: pipeline ETL transacional
- `sqlserver_schema.sql`: DDL + MERGE stored procedure
- `../sample-data/sample.json`: fallback local quando API falhar

## Dependências

```bash
pip install pandas sqlalchemy pyodbc requests python-dotenv
```

## Variáveis de ambiente (`.env`)

```env
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_SERVER=seu_servidor
DB_DATABASE=seu_banco
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_TRUST_SERVER_CERTIFICATE=yes
API_URL=https://sua-api.com/endpoint
API_TOKEN=seu_token
```

> A tabela `dbo.tabela_producao` deve existir antes de executar a procedure `dbo.MergeStagingToProducao`.

## Como rodar

```bash
python sync/etl.py
python sync/etl.py --truncate
```
