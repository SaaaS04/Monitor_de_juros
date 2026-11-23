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


def conectar():
    load_dotenv()
    return psycopg.connect(
        host="localhost",
        port=5432,
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def ler_processado():
    arquivos = sorted(PASTA_PROCESSED.glob("taxas_*.parquet"))
    if not arquivos:
        raise FileNotFoundError(f"Nenhum Parquet em {PASTA_PROCESSED}. Rode a transformação antes.")
    arquivo = arquivos[-1]
    df = pd.read_parquet(arquivo)
    linhas = list(df[COLUNAS].astype(object).itertuples(index=False, name=None))
    return arquivo, linhas


def carregar_stg(cur, linhas):
    cur.execute(ler_sql("create_stg_tax.sql"))
    cur.executemany(ler_sql("insert_stg_tax.sql"), linhas)
    return cur.rowcount


def atualizar_modelo(cur):
    cur.execute(ler_sql("create_model.sql"))
    cur.execute(ler_sql("populate_model.sql"))


def contar(cur, tabela):
    cur.execute(f"SELECT COUNT(*) FROM {tabela}")
    return cur.fetchone()[0]


def run():
    arquivo, linhas = ler_processado()

    with conectar() as conexao:
        with conexao.cursor() as cur:
            inseridas = carregar_stg(cur, linhas)
            atualizar_modelo(cur)
            bancos = contar(cur, "dim_bank")
            tipos = contar(cur, "dim_credit_type")
            taxas = contar(cur, "fact_rate")

    print(f"[load] {arquivo.name}: {len(linhas)} linhas lidas, {inseridas} novas na stg_tax")
    print(f"[load] Modelo: {bancos} bancos, {tipos} tipos de crédito, {taxas} taxas")


if __name__ == "__main__":
    run()