CREATE TABLE IF NOT EXISTS fact_selic (
    data          DATE           PRIMARY KEY,
    meta_selic    NUMERIC(6, 2)  NOT NULL,
    carregado_em  TIMESTAMP      NOT NULL DEFAULT now()
);