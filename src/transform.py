import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).parent.parent
PASTA_RAW = RAIZ / "data" / "raw"
PASTA_PROCESSED = RAIZ / "data" / "processed"

COLUNAS = {
    "InicioPeriodo": "inicio_periodo",
    "FimPeriodo": "fim_periodo",
    "codigoSegmento": "codigo_segmento",
    "Segmento": "segmento",
    "codigoModalidade": "codigo_modalidade",
    "Modalidade": "modalidade",
    "Posicao": "posicao",
    "InstituicaoFinanceira": "banco",
    "TaxaJurosAoMes": "taxa_mes",
    "TaxaJurosAoAno": "taxa_ano",
    "cnpj8": "cnpj8",
}

GRAO = ["inicio_periodo", "segmento", "modalidade", "cnpj8"]


def ler_bruto(arquivo):
    with open(arquivo, encoding="utf-8") as f:
        dados = json.load(f)
    return pd.DataFrame(dados["value"])


def limpar(df):
    df = df.rename(columns=COLUNAS)
    df["inicio_periodo"] = pd.to_datetime(df["inicio_periodo"], format="%Y-%m-%d")
    df["fim_periodo"] = pd.to_datetime(df["fim_periodo"], format="%Y-%m-%d")
    df["cnpj8"] = df["cnpj8"].astype(str).str.zfill(8)
    return df.drop(columns=["codigo_segmento", "codigo_modalidade", "posicao"])


def validar(df):
    duplicadas = df.duplicated(subset=GRAO).sum()
    if duplicadas > 0:
        raise ValueError(f"{duplicadas} linhas duplicadas no grão")

    nulos = df[GRAO + ["taxa_mes", "taxa_ano"]].isna().sum().sum()
    if nulos > 0:
        raise ValueError(f"{nulos} valores nulos em colunas obrigatórias")


def salvar(df, arquivo):
    PASTA_PROCESSED.mkdir(parents=True, exist_ok=True)
    destino = PASTA_PROCESSED / f"{arquivo.stem}.parquet"
    df.to_parquet(destino, index=False)
    return destino

def arquivos_pendentes():
    processados = {arquivo.stem for arquivo in PASTA_PROCESSED.glob("taxas_*.parquet")}
    return [
        arquivo
        for arquivo in sorted(PASTA_RAW.glob("taxas_*.json"))
        if arquivo.stem not in processados
    ]

def run():
    pendentes = arquivos_pendentes()
    print(f"[transform] {len(pendentes)} arquivos para tratar")

    for arquivo in pendentes:
        df = ler_bruto(arquivo)
        df = limpar(df)
        validar(df)
        destino = salvar(df, arquivo)
        print(f"[transform] {destino.name}: {len(df)} linhas")

if __name__ == "__main__":
    run()