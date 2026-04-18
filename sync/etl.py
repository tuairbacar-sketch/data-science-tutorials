import argparse
import hashlib
import json
import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from urllib3.util.retry import Retry


load_dotenv()


def get_engine():
    conn_url = URL.create(
        "mssql+pyodbc",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_SERVER"),
        database=os.getenv("DB_DATABASE"),
        query={
            "driver": os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server"),
            "TrustServerCertificate": os.getenv("DB_TRUST_SERVER_CERTIFICATE", "yes"),
        },
    )
    return create_engine(conn_url, fast_executemany=True)


def _fallback_sample_path() -> Path:
    return Path(__file__).resolve().parent.parent / "sample-data" / "sample.json"


def fetch_api_data():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        response = session.get(
            os.getenv("API_URL"),
            headers={"Authorization": f"Token token={os.getenv('API_TOKEN', '')}"},
            timeout=10,
        )
        response.raise_for_status()
        print("✅ Dados recebidos da API")
        return pd.DataFrame(response.json()), "API"
    except Exception as err:
        print(f"⚠️ Falha na API: {err}. Usando fallback local...")
        sample_path = _fallback_sample_path()
        with sample_path.open("r", encoding="utf-8") as sample_file:
            data = json.load(sample_file)
        return pd.DataFrame(data), "LOCAL"


def validate_df(df: pd.DataFrame) -> pd.DataFrame:
    print(f"Linhas recebidas: {len(df)}")

    if "id" in df.columns:
        df = df.drop_duplicates(subset=["id"], keep="last")

    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

    df = df.dropna(subset=["id"])

    df["payload"] = df.apply(lambda row: row.to_json(date_format="iso"), axis=1)
    df["hash_payload"] = df["payload"].apply(lambda payload: hashlib.sha256(payload.encode()).hexdigest())

    print(f"Linhas após validação: {len(df)}")
    return df[["id", "payload", "hash_payload"]]


def sync_etl(truncate=False):
    engine = get_engine()
    origem = "N/A"
    df = pd.DataFrame()
    df_staging = pd.DataFrame()

    with engine.begin() as conn:
        try:
            df, origem = fetch_api_data()
            if df.empty:
                raise ValueError("DataFrame vazio. Nada para inserir.")

            df_staging = validate_df(df)

            if truncate:
                conn.execute(text("TRUNCATE TABLE staging_raw"))
                print("🗑️ staging_raw limpa")

            df_staging.to_sql(
                name="staging_raw",
                con=conn,
                if_exists="append",
                index=False,
                chunksize=1000,
                method="multi",
            )
            print(f"✅ {len(df_staging)} linhas inseridas em staging_raw")

            result = conn.execute(text("EXEC dbo.MergeStagingToProducao"))
            merge_result = result.scalar()
            linhas_merge = int(merge_result or 0)
            print(f"✅ MERGE executado. {linhas_merge} linhas afetadas na produção")

            conn.execute(
                text(
                    """
                    INSERT INTO sync_log (status, origem_dados, total_linhas, data_execucao)
                    VALUES (:status, :origem, :total, GETDATE())
                    """
                ),
                {"status": "SUCESSO", "origem": origem, "total": len(df_staging)},
            )
        except Exception as err:
            print(f"↩️ Erro: {err}. Rollback executado.")
            try:
                with engine.begin() as conn_err:
                    conn_err.execute(
                        text(
                            """
                            INSERT INTO sync_log (status, origem_dados, total_linhas, erro_msg, data_execucao)
                            VALUES ('ERRO', :origem, :total, :erro, GETDATE())
                            """
                        ),
                        {
                            "origem": origem,
                            "total": len(df_staging) if not df_staging.empty else len(df),
                            "erro": str(err),
                        },
                    )
            except Exception as log_err:
                print(f"⚠️ Falha ao registrar erro em sync_log: {log_err}")
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--truncate", action="store_true", help="Limpa staging antes")
    args = parser.parse_args()

    sync_etl(truncate=args.truncate)
