WITH medianas AS (
    SELECT
        c.segmento,
        c.modalidade,
        g.grupo,
        COUNT(*) AS bancos,
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY f.taxa_mes)::numeric, 2) AS mediana
    FROM fact_rate AS f
    JOIN dim_credit_type AS c ON c.credit_type_id = f.credit_type_id
    JOIN ref_bank_group AS g ON g.cnpj8 = f.cnpj8
    WHERE f.inicio_periodo = (SELECT MAX(inicio_periodo) FROM fact_rate)
    GROUP BY c.segmento, c.modalidade, g.grupo
)
SELECT
    d.segmento,
    d.modalidade,
    d.bancos AS n_digital,
    d.mediana AS digital,
    t.bancos AS n_tradicional,
    t.mediana AS tradicional,
    d.mediana - t.mediana AS diferenca
FROM medianas AS d
JOIN medianas AS t
  ON t.segmento = d.segmento
 AND t.modalidade = d.modalidade
 AND t.grupo = 'tradicional'
WHERE d.grupo = 'digital'
ORDER BY d.segmento, diferenca;