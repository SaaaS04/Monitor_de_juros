INSERT INTO stg_tax (
    inicio_periodo, fim_periodo, segmento, modalidade,
    banco, cnpj8, taxa_mes, taxa_ano
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (inicio_periodo, segmento, modalidade, cnpj8) DO NOTHING;