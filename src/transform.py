import json
from pathlib import Path

import pandas as pd

PASTA_RAW = Path(__file__).parent.parent / "data" / "raw"
PASTA_PROCESSED = Path(__file__).parent.parent / "data" / "processed"

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

arquivo = sorted(PASTA_RAW.glob("taxas_*.json"))[-1]

with open(arquivo, encoding="utf-8") as f:
    dados = json.load(f)

df = pd.DataFrame(dados["value"])
df = df.rename(columns=COLUNAS)

df["inicio_periodo"] = pd.to_datetime(df["inicio_periodo"], format="%Y-%m-%d")
df["fim_periodo"] = pd.to_datetime(df["fim_periodo"], format="%Y-%m-%d")

df["cnpj8"] = df["cnpj8"].astype(str).str.zfill(8)

df = df.drop(columns=["codigo_segmento", "codigo_modalidade", "posicao"])

duplicadas = df.duplicated(subset=GRAO).sum()
if duplicadas > 0:
    raise ValueError(f"{duplicadas} linhas duplicadas no grão")

nulos = df[GRAO + ["taxa_mes", "taxa_ano"]].isna().sum().sum()
if nulos > 0:
    raise ValueError(f"{nulos} valores nulos em colunas obrigatórias")

PASTA_PROCESSED.mkdir(parents=True, exist_ok=True)

destino = PASTA_PROCESSED / f"{arquivo.stem}.parquet"
df.to_parquet(destino, index=False)

print(f"{len(df)} linhas salvas em {destino}")
