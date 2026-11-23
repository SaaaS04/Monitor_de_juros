SELECT
    c.segmento,
    c.modalidade,
    COUNT(*) AS bancos,
    MIN(f.taxa_mes) AS minima,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY f.taxa_mes)::numeric, 2) AS mediana,    MAX(f.taxa_mes) AS maxima
FROM fact_rate AS f
JOIN dim_credit_type AS c ON c.credit_type_id = f.credit_type_id
WHERE f.inicio_periodo = (SELECT MAX(inicio_periodo) FROM fact_rate)
GROUP BY c.segmento, c.modalidade
ORDER BY c.segmento, mediana DESC;