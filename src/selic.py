import json
from datetime import date
from pathlib import Path

import pandas as pd
import requests

from load import conectar, ler_sql

URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados"
INICIO = date(2024, 10, 1)
ARQUIVO_RAW = Path(__file__).parent.parent / "data" / "raw" / "selic.json"


def extrair():
    params = {
        "formato": "json",
        "dataInicial": INICIO.strftime("%d/%m/%Y"),
        "dataFinal": date.today().strftime("%d/%m/%Y"),
    }
    response = requests.get(URL, params=params, timeout=60)
    response.raise_for_status()
    dados = response.json()

    ARQUIVO_RAW.parent.mkdir(parents=True, exist_ok=True)
    with open(ARQUIVO_RAW, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    return dados


def transformar(dados):
    df = pd.DataFrame(dados)
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
    df["valor"] = pd.to_numeric(df["valor"])
    df = df.rename(columns={"valor": "meta_selic"})

    if df["data"].duplicated().any():
        raise ValueError("Datas duplicadas na série da Selic")
    return df


def carregar(df):
    linhas = list(df[["data", "meta_selic"]].astype(object).itertuples(index=False, name=None))
    with conectar() as conexao:
        with conexao.cursor() as cur:
            cur.execute(ler_sql("create_selic.sql"))
            cur.executemany(ler_sql("insert_selic.sql"), linhas)
            return cur.rowcount


def run():
    dados = extrair()
    df = transformar(dados)
    novas = carregar(df)
    print(f"[selic] {len(df)} dias lidos, {novas} novos, de {df['data'].min():%d/%m/%Y} a {df['data'].max():%d/%m/%Y}")


if __name__ == "__main__":
    run()