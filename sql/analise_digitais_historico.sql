WITH medianas AS (
    SELECT
        f.inicio_periodo,
        c.segmento,
        c.modalidade,
        g.grupo,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY f.taxa_mes) AS mediana
    FROM fact_rate AS f
    JOIN dim_credit_type AS c ON c.credit_type_id = f.credit_type_id
    JOIN ref_bank_group AS g ON g.cnpj8 = f.cnpj8
    GROUP BY f.inicio_periodo, c.segmento, c.modalidade, g.grupo
),
comparacao AS (
    SELECT
        d.inicio_periodo,
        d.segmento,
        d.modalidade,
        d.mediana - t.mediana AS diferenca
    FROM medianas AS d
    JOIN medianas AS t
      ON t.inicio_periodo = d.inicio_periodo
     AND t.segmento = d.segmento
     AND t.modalidade = d.modalidade
     AND t.grupo = 'tradicional'
    WHERE d.grupo = 'digital'
)
SELECT
    segmento,
    modalidade,
    COUNT(*) AS periodos,
    COUNT(*) FILTER (WHERE diferenca > 0) AS digital_mais_caro,
    ROUND(100.0 * COUNT(*) FILTER (WHERE diferenca > 0) / COUNT(*)) AS pct_mais_caro,
    ROUND(AVG(diferenca)::numeric, 2) AS diferenca_media
FROM comparacao
GROUP BY segmento, modalidade
ORDER BY segmento, diferenca_media;