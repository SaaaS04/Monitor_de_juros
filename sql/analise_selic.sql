WITH taxas_mensais AS (
    SELECT
        date_trunc('month', f.inicio_periodo)::date AS mes,
        c.segmento,
        c.modalidade,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY f.taxa_ano) AS mediana_ano
    FROM fact_rate AS f
    JOIN dim_credit_type AS c ON c.credit_type_id = f.credit_type_id
    GROUP BY 1, 2, 3
),
selic_mensal AS (
    SELECT
        date_trunc('month', data)::date AS mes,
        AVG(meta_selic) AS selic
    FROM fact_selic
    GROUP BY 1
)
SELECT
    t.segmento,
    t.modalidade,
    COUNT(*) AS meses,
    ROUND(CORR(s.selic, t.mediana_ano)::numeric, 2) AS correlacao,
    ROUND(AVG(t.mediana_ano - s.selic)::numeric, 1) AS spread_medio
FROM taxas_mensais AS t
JOIN selic_mensal AS s ON s.mes = t.mes
GROUP BY t.segmento, t.modalidade
ORDER BY correlacao DESC;