import requests
import pandas as pd

url = "https://olinda.bcb.gov.br/olinda/servico/taxaJuros/versao/v2/odata/TaxasJurosDiariaPorInicioPeriodo"

PARAMS = {
    "$top": 100,
    "$format": "json",
}
response = requests.get(url, params=PARAMS, timeout=30)
response.raise_for_status()

dados_api = response.json()
registros = dados_api["value"]

df = pd.DataFrame(registros)

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

print(df.shape)
print()
print(df.dtypes)
print()
print(df.head())
print()
print(df["Modalidade"].value_counts())
print()
print(df["InstituicaoFinanceira"].nunique())    