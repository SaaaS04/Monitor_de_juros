import os
from pathlib import Path

import pandas as pd
import psycopg
from dotenv import load_dotenv

RAIZ = Path(__file__).parent.parent
PASTA_SQL = RAIZ / "sql"
PASTA_PROCESSED = RAIZ / "data" / "processed"

COLUNAS = [
    "inicio_periodo", "fim_periodo", "segmento", "modalidade",
    "banco", "cnpj8", "taxa_mes", "taxa_ano",
]


def ler_sql(nome):
    return (PASTA_SQL / nome).read_text(encoding="utf-8")


load_dotenv()

arquivos = sorted(PASTA_PROCESSED.glob("taxas_*.parquet"))
if not arquivos:
    raise FileNotFoundError(f"Nenhum Parquet em {PASTA_PROCESSED}. Rode a transformação antes.")
arquivo = arquivos[-1]

df = pd.read_parquet(arquivo)
linhas = list(df[COLUNAS].astype(object).itertuples(index=False, name=None))

conexao = psycopg.connect(
    host="localhost",
    port=5432,
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)

with conexao.cursor() as cur:
    cur.execute(ler_sql("create_stg_tax.sql"))
    cur.executemany(ler_sql("insert_stg_tax.sql"), linhas)
    inseridas = cur.rowcount

    cur.execute(ler_sql("create_model.sql"))
    cur.execute(ler_sql("populate_model.sql"))

    cur.execute("SELECT COUNT(*) FROM dim_bank")
    bancos = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM dim_credit_type")
    tipos = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM fact_rate")
    taxas = cur.fetchone()[0]

conexao.commit()
conexao.close()

print(f"{arquivo.name}: {len(linhas)} linhas lidas, {inseridas} novas na stg_tax")
print(f"Modelo: {bancos} bancos, {tipos} tipos de crédito, {taxas} taxas")