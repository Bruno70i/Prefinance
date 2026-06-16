-- migrations/2026_validacoes.sql
-- Migração aditiva e idempotente para suportar validações de robustez.

-- 1) Novas colunas em entidades
ALTER TABLE entidades
    ADD COLUMN IF NOT EXISTS cpf_representante VARCHAR(14) NULL,
    ADD COLUMN IF NOT EXISTS telefone VARCHAR(20) NULL,
    ADD COLUMN IF NOT EXISTS cnpj_raiz  VARCHAR(8)  NULL,
    ADD COLUMN IF NOT EXISTS cnpj_ordem VARCHAR(4)  NULL;

COMMENT ON COLUMN entidades.cpf_representante IS 'CPF do representante (apenas dígitos). NÃO único: a mesma pessoa pode representar vários CNPJs.';
COMMENT ON COLUMN entidades.telefone IS 'Telefone de contato (apenas dígitos).';
COMMENT ON COLUMN entidades.cnpj_raiz IS 'Primeiros 8 dígitos do CNPJ (raiz do grupo econômico).';
COMMENT ON COLUMN entidades.cnpj_ordem IS 'Dígitos 9-12 do CNPJ (0001=matriz, 0002+=filial).';

-- 2) Índices (NÃO únicos para CPF e raiz, pois repetição é esperada)
CREATE INDEX IF NOT EXISTS idx_entidades_cpf_representante ON entidades (cpf_representante);
CREATE INDEX IF NOT EXISTS idx_entidades_cnpj_raiz        ON entidades (cnpj_raiz);

-- 3) Índice ÚNICO sobre o CNPJ normalizado (dígitos). Garante unicidade real mesmo que
--    alguém grave com/sem pontuação. Usa expressão para ignorar formatação.
CREATE UNIQUE INDEX IF NOT EXISTS uq_entidades_cnpj_digitos
    ON entidades (regexp_replace(cnpj, '\D', '', 'g'))
    WHERE cnpj IS NOT NULL;

-- 4) Backfill: extrai CPF/telefone do JSONB e popula raiz/ordem a partir do CNPJ existente.
UPDATE entidades
SET cpf_representante = regexp_replace(configuracoes_extras->>'cpf_representante', '\D', '', 'g')
WHERE cpf_representante IS NULL
  AND configuracoes_extras->>'cpf_representante' IS NOT NULL
  AND configuracoes_extras->>'cpf_representante' <> '';

UPDATE entidades
SET telefone = regexp_replace(configuracoes_extras->>'telefone', '\D', '', 'g')
WHERE telefone IS NULL
  AND configuracoes_extras->>'telefone' IS NOT NULL
  AND configuracoes_extras->>'telefone' <> '';

UPDATE entidades
SET cnpj_raiz  = substring(regexp_replace(cnpj, '\D', '', 'g') from 1 for 8),
    cnpj_ordem = substring(regexp_replace(cnpj, '\D', '', 'g') from 9 for 4)
WHERE cnpj IS NOT NULL
  AND length(regexp_replace(cnpj, '\D', '', 'g')) = 14;
