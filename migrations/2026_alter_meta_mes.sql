-- migrations/2026_alter_meta_mes.sql
-- Altera a coluna meta_mes_atendimentos da tabela dados_parceria de INTEGER para VARCHAR(255)
-- para suportar textos livres (como "960 Atendimentos").

ALTER TABLE dados_parceria ALTER COLUMN meta_mes_atendimentos TYPE VARCHAR(255) USING meta_mes_atendimentos::varchar;
