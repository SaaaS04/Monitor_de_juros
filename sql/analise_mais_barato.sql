WITH ranking AS (
    SELECT
        c.segmento,
        c.modalidade,
        b.banco,
        f.taxa_mes,
        RANK() OVER (PARTITION BY f.credit_type_id ORDER BY f.taxa_mes ASC) AS posicao
    FROM fact_rate AS f
    JOIN dim_bank AS b ON b.cnpj8 = f.cnpj8
    JOIN dim_credit_type AS c ON c.credit_type_id = f.credit_type_id
    WHERE f.inicio_periodo = (SELECT MAX(inicio_periodo) FROM fact_rate)
)
SELECT segmento, modalidade, banco, taxa_mes
FROM ranking
WHERE posicao = 1
ORDER BY segmento, modalidade;