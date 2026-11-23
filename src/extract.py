import json
import time
from datetime import date, timedelta
from pathlib import Path

import requests

URL = "https://olinda.bcb.gov.br/olinda/servico/taxaJuros/versao/v2/odata/TaxasJurosDiariaPorInicioPeriodo"
LIMITE = 10000
INICIO_HISTORICO = date(2025, 1, 1)
PASTA_RAW = Path(__file__).parent.parent / "data" / "raw"


def buscar_periodo_mais_recente():
    params = "$top=1&$orderby=InicioPeriodo%20desc&$select=InicioPeriodo&$format=json"
    response = requests.get(URL, params=params, timeout=30)
    response.raise_for_status()
    return date.fromisoformat(response.json()["value"][0]["InicioPeriodo"])


def periodos_ja_extraidos():
    return {
        date.fromisoformat(arquivo.stem.removeprefix("taxas_"))
        for arquivo in PASTA_RAW.glob("taxas_*.json")
    }


def periodos_faltando(mais_recente):
    extraidos = periodos_ja_extraidos()
    faltando = []
    dia = INICIO_HISTORICO
    while dia <= mais_recente:
        if dia.weekday() < 5 and dia not in extraidos:
            faltando.append(dia)
        dia += timedelta(days=1)
    return faltando


def baixar_periodo(inicio):
    params = f"$filter=InicioPeriodo%20eq%20'{inicio.isoformat()}'&$top={LIMITE}&$format=json"
    response = requests.get(URL, params=params, timeout=60)
    response.raise_for_status()

    dados = response.json()
    if len(dados["value"]) == LIMITE:
        raise ValueError(f"{inicio}: a API devolveu o limite de {LIMITE} linhas, o período pode estar incompleto")
    return dados


def salvar_bruto(dados, inicio):
    PASTA_RAW.mkdir(parents=True, exist_ok=True)
    arquivo = PASTA_RAW / f"taxas_{inicio.isoformat()}.json"
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def run():
    mais_recente = buscar_periodo_mais_recente()
    faltando = periodos_faltando(mais_recente)
    print(f"[extract] {len(faltando)} dias para verificar até {mais_recente}")

    novos = 0
    for dia in faltando:
        dados = baixar_periodo(dia)
        if dados["value"]:
            salvar_bruto(dados, dia)
            novos += 1
            print(f"[extract] {dia}: {len(dados['value'])} registros")
        else:
            print(f"[extract] {dia}: sem dados (feriado?)")
        time.sleep(1)

    print(f"[extract] {novos} períodos novos salvos")


if __name__ == "__main__":
    run()