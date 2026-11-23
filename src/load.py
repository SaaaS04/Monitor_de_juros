import os
from datetime import date
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


def periodo_do_arquivo(arquivo):
    return date.fromisoformat(arquivo.stem.removeprefix("taxas_"))


def periodos_carregados(cur):
    cur.execute("SELECT DISTINCT inicio_periodo FROM stg_tax")
    return {linha[0] for linha in cur.fetchall()}


def arquivos_pendentes(cur):
    carregados = periodos_carregados(cur)
    return [
        arquivo
        for arquivo in sorted(PASTA_PROCESSED.glob("taxas_*.parquet"))
        if periodo_do_arquivo(arquivo) not in carregados
    ]


def ler_linhas(arquivo):
    df = pd.read_parquet(arquivo)
    return list(df[COLUNAS].astype(object).itertuples(index=False, name=None))


def atualizar_modelo(cur):
    cur.execute(ler_sql("create_model.sql"))
    cur.execute(ler_sql("populate_model.sql"))
    cur.execute(ler_sql("seed_bank_group.sql"))


def contar(cur, tabela):
    cur.execute(f"SELECT COUNT(*) FROM {tabela}")
    return cur.fetchone()[0]


def run():
    with conectar() as conexao:
        with conexao.cursor() as cur:
            cur.execute(ler_sql("create_stg_tax.sql"))

            pendentes = arquivos_pendentes(cur)
            print(f"[load] {len(pendentes)} períodos para carregar")

            sql_inserir = ler_sql("insert_stg_tax.sql")
            for arquivo in pendentes:
                linhas = ler_linhas(arquivo)
                cur.executemany(sql_inserir, linhas)
                print(f"[load] {arquivo.name}: {cur.rowcount} linhas")

            atualizar_modelo(cur)
            bancos = contar(cur, "dim_bank")
            tipos = contar(cur, "dim_credit_type")
            taxas = contar(cur, "fact_rate")

    print(f"[load] Modelo: {bancos} bancos, {tipos} tipos de crédito, {taxas} taxas")


if __name__ == "__main__":
    run()