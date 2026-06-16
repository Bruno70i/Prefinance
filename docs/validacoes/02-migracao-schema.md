# Passo 02 — Migração de schema: CPF, telefone e raiz/ordem do CNPJ

> **Objetivo:** tornar **CPF do representante** e **telefone** colunas próprias e indexáveis (hoje
> só existem dentro do JSONB `configuracoes_extras`), e adicionar `cnpj_raiz`/`cnpj_ordem` para
> agrupar matriz/filial. Sem isso, os passos 06, 07 e 08 são impossíveis (não há como consultar
> "CPF vinculado a quais CNPJs").
>
> A migração é **idempotente** (`IF NOT EXISTS`) e **não destrói dados** — apenas adiciona colunas
> e faz backfill a partir do JSONB. O app continua lendo `configuracoes_extras` como antes.

**Depende de:** nada (mas é pré-requisito de 06, 07, 08).
**Arquivos novos:** `migrations/2026_validacoes.sql`, `run_migration.py`.
**Arquivos alterados:** `main.py` (persistir CPF/telefone nas novas colunas no create/update).

---

## 2.1 SQL da migração — `migrations/2026_validacoes.sql`

```sql
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
--    (Só cria se ainda não houver duplicatas; ver nota na seção 2.4.)
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
```

---

## 2.2 Runner — `run_migration.py`

Modelado no padrão de conexão de `clear_db.py`. Recebe o caminho do `.sql` por argumento.

```python
# run_migration.py
# Uso: python run_migration.py migrations/2026_validacoes.sql
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "prefinance")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)

if len(sys.argv) < 2:
    print("Uso: python run_migration.py <caminho_do_arquivo.sql>")
    sys.exit(1)

caminho = sys.argv[1]
with open(caminho, "r", encoding="utf-8") as f:
    sql = f.read()

print(f"Aplicando migração: {caminho} em {DB_HOST}:{DB_PORT}/{DB_NAME}")
try:
    engine = create_engine(DATABASE_URL)
    with engine.begin() as conn:
        conn.execute(text(sql))
    print("Migração aplicada com sucesso.")
except Exception as err:
    print(f"Erro ao aplicar migração: {err}")
    sys.exit(1)
```

Execução:
```bash
python run_migration.py migrations/2026_validacoes.sql
```

---

## 2.3 Persistir CPF/telefone/raiz/ordem no backend (`main.py`)

A partir de agora, o create/update deve **gravar também nas colunas novas** (mantendo o JSONB por
compatibilidade). São edições cirúrgicas.

### a) `create_entidade` (~linha 237)
No `INSERT INTO entidades (...)`, **adicione** as colunas e binds:

```python
# Antes de montar o INSERT, derive raiz/ordem e normalize o CPF:
import re
_cnpj_digitos = re.sub(r"\D", "", entidade.cnpj or "")
_cnpj_raiz  = _cnpj_digitos[0:8]  if len(_cnpj_digitos) == 14 else None
_cnpj_ordem = _cnpj_digitos[8:12] if len(_cnpj_digitos) == 14 else None

_extras = entidade.configuracoes_extras or {}
_cpf_rep = re.sub(r"\D", "", str(_extras.get("cpf_representante") or "")) or None
_telefone = re.sub(r"\D", "", str(_extras.get("telefone") or "")) or None
```

Acrescente no SQL (lista de colunas e de valores) e no dict de binds:
```
..., cpf_representante, telefone, cnpj_raiz, cnpj_ordem
..., :cpf_representante, :telefone, :cnpj_raiz, :cnpj_ordem
```
```python
"cpf_representante": _cpf_rep,
"telefone": _telefone,
"cnpj_raiz": _cnpj_raiz,
"cnpj_ordem": _cnpj_ordem,
```

### b) `update_entidade` (~linha 531)
No `UPDATE entidades SET ...`, adicione os mesmos campos:
```
cpf_representante = :cpf_representante,
telefone = :telefone,
cnpj_raiz = :cnpj_raiz,
cnpj_ordem = :cnpj_ordem,
```
E os mesmos binds (derivados da mesma forma que em `create_entidade`).

> **Importante:** o CPF continua sendo enviado pelo front dentro de `configuracoes_extras`
> (não muda o contrato do front neste passo). O backend é quem **espelha** para a coluna. Assim,
> nenhum form quebra.

---

## 2.4 Critérios de aceite

- [ ] `python run_migration.py migrations/2026_validacoes.sql` roda sem erro e é **idempotente**
      (rodar 2x não falha).
- [ ] `\d entidades` no psql mostra as 4 colunas novas e os índices.
- [ ] Cadastrar uma entidade nova com CPF preenchido → a coluna `cpf_representante` fica
      preenchida com **só dígitos**; `cnpj_raiz`/`cnpj_ordem` corretos.
- [ ] Dados antigos foram backfilled (CPF que estava no JSONB agora aparece na coluna).

## 2.5 Segurança / reversão

- A migração não remove nada. Para reverter (raro): `ALTER TABLE entidades DROP COLUMN ...` e
  `DROP INDEX ...`.
- **Atenção ao índice único `uq_entidades_cnpj_digitos`:** se o banco **já tiver CNPJs duplicados**
  (com/sem pontuação), a criação do índice **falha**. Antes de criar, rode a consulta de
  diagnóstico abaixo e resolva duplicatas manualmente; ou comente a etapa 3 do SQL e crie o índice
  num segundo momento.

```sql
SELECT regexp_replace(cnpj,'\D','','g') AS cnpj_norm, count(*)
FROM entidades WHERE cnpj IS NOT NULL
GROUP BY 1 HAVING count(*) > 1;
```

> Próximo: `03-cnpj-duplicado.md`.
