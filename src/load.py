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

load_dotenv()

arquivo = sorted(PASTA_PROCESSED.glob("taxas_*.parquet"))[-1]
df = pd.read_parquet(arquivo)

linhas = list(df[COLUNAS].astype(object).itertuples(index=False, name=None))

sql_criar = (PASTA_SQL / "create_stg_tax.sql").read_text(encoding="utf-8")
sql_inserir = (PASTA_SQL / "insert_stg_tax.sql").read_text(encoding="utf-8")

conexao = psycopg.connect(
    host="localhost",
    port=5432,
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)

with conexao.cursor() as cur:
    cur.execute(sql_criar)
    cur.executemany(sql_inserir, linhas)
    inseridas = cur.rowcount

conexao.commit()
conexao.close()

print(f"{arquivo.name}: {len(linhas)} linhas lidas, {inseridas} inseridas, {len(linhas) - inseridas} já existiam")