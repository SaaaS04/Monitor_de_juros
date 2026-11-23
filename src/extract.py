import json
from pathlib import Path

import requests

URL = "https://olinda.bcb.gov.br/olinda/servico/taxaJuros/versao/v2/odata/TaxasJurosDiariaPorInicioPeriodo"
LIMITE = 10000
PASTA_RAW = Path(__file__).parent.parent / "data" / "raw"


def buscar_periodo_mais_recente():
    params = "$top=1&$orderby=InicioPeriodo%20desc&$select=InicioPeriodo,FimPeriodo&$format=json"
    response = requests.get(URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()["value"][0]["InicioPeriodo"]


def baixar_periodo(inicio):
    params = f"$filter=InicioPeriodo%20eq%20'{inicio}'&$top={LIMITE}&$format=json"
    response = requests.get(URL, params=params, timeout=60)
    response.raise_for_status()

    dados = response.json()
    if len(dados["value"]) == LIMITE:
        raise ValueError(f"A API devolveu o limite de {LIMITE} linhas, o período pode estar incompleto")
    return dados


def salvar_bruto(dados, inicio):
    PASTA_RAW.mkdir(parents=True, exist_ok=True)
    arquivo = PASTA_RAW / f"taxas_{inicio}.json"
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    return arquivo


def run():
    inicio = buscar_periodo_mais_recente()
    dados = baixar_periodo(inicio)
    arquivo = salvar_bruto(dados, inicio)
    print(f"[extract] {len(dados['value'])} registros salvos em {arquivo.name}")


if __name__ == "__main__":
    run()