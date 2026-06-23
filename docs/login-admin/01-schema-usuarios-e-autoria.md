# Passo 01 — Migração: tabela `usuarios` + autoria em `entidades`

> **Objetivo:** criar a tabela de usuários e a coluna que guarda **quem criou** cada parceria. A
> migração é **idempotente** e **não destrói dados**.

**Depende de:** nada.
**Arquivos novos:** `migrations/2026_login.sql`.
**Arquivos alterados:** nenhum (rodar via runner existente `run_migration.py`).

---

## 1.1 SQL — `migrations/2026_login.sql`

```sql
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

-- (Sugestão — opcional) também registrar quem editou por último:
ALTER TABLE entidades
    ADD COLUMN IF NOT EXISTS atualizado_por VARCHAR(160) NULL;
```

## 1.2 Aplicar

```bash
python run_migration.py migrations/2026_login.sql
```
(`run_migration.py` já existe no projeto, do plano de validações.)

---

## 1.3 Critérios de aceite

- [ ] `\d usuarios` mostra a tabela com `username` único e `senha_hash`.
- [ ] `\d entidades` mostra a coluna `criado_por` (e `atualizado_por`, se incluída).
- [ ] Rodar a migração 2x não dá erro (idempotente).
- [ ] Dados existentes intactos (parcerias antigas ficam com `criado_por = NULL`).

## 1.4 Segurança / reversão

Aditivo. Reverter = `DROP TABLE usuarios;` e `ALTER TABLE entidades DROP COLUMN criado_por;`.

> Próximo: `02-backend-auth-core-e-login.md`.
