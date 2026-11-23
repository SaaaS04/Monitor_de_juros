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
        mes,
        selic,
        LAG(selic, 1) OVER (ORDER BY mes) AS selic_1m,
        LAG(selic, 2) OVER (ORDER BY mes) AS selic_2m,
        LAG(selic, 3) OVER (ORDER BY mes) AS selic_3m
    FROM (
        SELECT date_trunc('month', data)::date AS mes, AVG(meta_selic) AS selic
        FROM fact_selic
        GROUP BY 1
    ) AS s
)
SELECT
    t.segmento,
    t.modalidade,
    ROUND(CORR(s.selic, t.mediana_ano)::numeric, 2) AS mesmo_mes,
    ROUND(CORR(s.selic_1m, t.mediana_ano)::numeric, 2) AS "1_mes",
    ROUND(CORR(s.selic_2m, t.mediana_ano)::numeric, 2) AS "2_meses",
    ROUND(CORR(s.selic_3m, t.mediana_ano)::numeric, 2) AS "3_meses"
FROM taxas_mensais AS t
JOIN selic_mensal AS s ON s.mes = t.mes
GROUP BY t.segmento, t.modalidade
ORDER BY mesmo_mes DESC;