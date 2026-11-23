CREATE TABLE IF NOT EXISTS dim_bank (
    cnpj8          CHAR(8)    PRIMARY KEY,
    banco          TEXT       NOT NULL,
    atualizado_em  TIMESTAMP  NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS dim_credit_type (
    credit_type_id  INTEGER  GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    segmento        TEXT     NOT NULL,
    modalidade      TEXT     NOT NULL,
    UNIQUE (segmento, modalidade)
);

CREATE TABLE IF NOT EXISTS fact_rate (
    inicio_periodo  DATE            NOT NULL,
    fim_periodo     DATE            NOT NULL,
    cnpj8           CHAR(8)         NOT NULL REFERENCES dim_bank (cnpj8),
    credit_type_id  INTEGER         NOT NULL REFERENCES dim_credit_type (credit_type_id),
    taxa_mes        NUMERIC(10, 4)  NOT NULL,
    taxa_ano        NUMERIC(10, 4)  NOT NULL,
    PRIMARY KEY (inicio_periodo, credit_type_id, cnpj8)
);