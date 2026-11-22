import requests
import json
from pathlib import Path

URL = "https://olinda.bcb.gov.br/olinda/servico/taxaJuros/versao/v2/odata/TaxasJurosDiariaPorInicioPeriodo"

params = "$top=1&$orderby=InicioPeriodo%20desc&$select=InicioPeriodo,FimPeriodo&$format=json"
response = requests.get(URL, params=params, timeout=30)
response.raise_for_status()

registro = response.json()["value"][0]
print(registro)

inicio = registro["InicioPeriodo"]

params_periodo = f"$filter=InicioPeriodo%20eq%20'{inicio}'&$top=10000&$format=json"

response = requests.get(URL, params=params_periodo, timeout=60)
response.raise_for_status()

registros = response.json()["value"]

if len(registros) == 10000:
    raise ValueError("A API devolveu o limite de 10000 linhas, o período pode estar incompleto")

pasta = Path(__file__).parent.parent / "data" / "raw"
pasta.mkdir(parents=True, exist_ok=True)

arquivo = pasta / f"taxas_{inicio}.json"

with open(arquivo, "w", encoding="utf-8") as f:
    json.dump(response.json(), f, ensure_ascii=False, indent=2)

print(f"{len(registros)} registros salvos em {arquivo}")