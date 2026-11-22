CREATE TABLE IF NOT EXISTS stg_tax (
    inicio_periodo  DATE           NOT NULL,
    fim_periodo     DATE           NOT NULL,
    segmento        TEXT           NOT NULL,
    modalidade      TEXT           NOT NULL,
    banco           TEXT           NOT NULL,
    cnpj8           CHAR(8)        NOT NULL,
    taxa_mes        NUMERIC(10, 4) NOT NULL,
    taxa_ano        NUMERIC(10, 4) NOT NULL,
    carregado_em    TIMESTAMP      NOT NULL DEFAULT now(),
    PRIMARY KEY (inicio_periodo, segmento, modalidade, cnpj8)
);