-- migrations/2026_login.sql  (idempotente)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Usuários comuns do sistema (o admin NÃO fica aqui; vem do .env)
CREATE TABLE IF NOT EXISTS usuarios (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username    VARCHAR(80)  UNIQUE NOT NULL,
    nome        VARCHAR(160) NOT NULL,
    senha_hash  TEXT         NOT NULL,
    ativo       BOOLEAN      NOT NULL DEFAULT TRUE,
    criado_em   TIMESTAMPTZ  DEFAULT CURRENT_TIMESTAMP,
    ultimo_login TIMESTAMPTZ NULL
);
COMMENT ON TABLE usuarios IS 'Usuários comuns. O administrador é definido no .env (LOGIN/SENHA).';

-- Autoria do cadastro: nome de quem criou (snapshot). created_at já existe em entidades.
ALTER TABLE entidades
    ADD COLUMN IF NOT EXISTS criado_por VARCHAR(160) NULL;
COMMENT ON COLUMN entidades.criado_por IS 'Nome do usuário que criou a parceria (snapshot).';

-- também registrar quem editou por último:
ALTER TABLE entidades
    ADD COLUMN IF NOT EXISTS atualizado_por VARCHAR(160) NULL;
COMMENT ON COLUMN entidades.atualizado_por IS 'Nome do usuário que atualizou a parceria pela última vez.';
