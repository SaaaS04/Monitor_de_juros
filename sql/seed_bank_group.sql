CREATE TABLE IF NOT EXISTS ref_bank_group (
    cnpj8  CHAR(8)  PRIMARY KEY REFERENCES dim_bank (cnpj8),
    grupo  TEXT     NOT NULL CHECK (grupo IN ('digital', 'tradicional'))
);

DELETE FROM ref_bank_group;

INSERT INTO ref_bank_group (cnpj8, grupo)
SELECT v.cnpj8, v.grupo
FROM (VALUES
    ('00416968', 'digital'),
    ('31872495', 'digital'),
    ('61348538', 'digital'),
    ('30680829', 'digital'),
    ('37679449', 'digital'),
    ('09516419', 'digital'),
    ('00000000', 'tradicional'),
    ('00360305', 'tradicional'),
    ('60701190', 'tradicional'),
    ('60872504', 'tradicional'),
    ('60746948', 'tradicional'),
    ('07207996', 'tradicional'),
    ('90400888', 'tradicional')
) AS v (cnpj8, grupo)
WHERE EXISTS (
    SELECT 1 FROM dim_bank AS b WHERE b.cnpj8 = v.cnpj8
);