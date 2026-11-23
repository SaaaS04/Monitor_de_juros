INSERT INTO dim_bank (cnpj8, banco)
SELECT DISTINCT ON (cnpj8) cnpj8, banco
FROM stg_tax
ORDER BY cnpj8, inicio_periodo DESC
ON CONFLICT (cnpj8) DO UPDATE
SET banco = EXCLUDED.banco,
    atualizado_em = now()
WHERE dim_bank.banco <> EXCLUDED.banco;

INSERT INTO dim_credit_type (segmento, modalidade)
SELECT DISTINCT segmento, modalidade
FROM stg_tax
ON CONFLICT (segmento, modalidade) DO NOTHING;

INSERT INTO fact_rate (inicio_periodo, fim_periodo, cnpj8, credit_type_id, taxa_mes, taxa_ano)
SELECT s.inicio_periodo, s.fim_periodo, s.cnpj8, c.credit_type_id, s.taxa_mes, s.taxa_ano
FROM stg_tax AS s
JOIN dim_credit_type AS c
  ON c.segmento = s.segmento
 AND c.modalidade = s.modalidade
ON CONFLICT (inicio_periodo, credit_type_id, cnpj8) DO NOTHING;