INSERT INTO fact_selic (data, meta_selic)
VALUES (%s, %s)
ON CONFLICT (data) DO NOTHING;