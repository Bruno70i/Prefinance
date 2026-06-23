# Plano — Login, Painel Admin e Autoria dos cadastros

> **Objetivo:** adicionar (1) **login** simples (usuário e senha); (2) um **painel admin em `/admin`**
> onde o gestor adiciona/edita/exclui usuários e **redefine senhas** (a "recuperação de senha"); o
> **admin vem do `.env`** (`LOGIN`/`SENHA`) — mudou o `.env`, mudou o acesso admin; (3) **autoria**:
> cada parceria mostra **quem a criou** e, ao clicar no nome, **a data e hora** de criação.
>
> **Para quem vai implementar (IA/dev):** leia este índice antes de começar. Os passos são
> **incrementais**; na ordem abaixo o site continua funcionando. Toda a lógica nova vai em **arquivos
> novos**; `main.py` ganha rotas e os endpoints de dados ganham proteção.

---

## 0. Decisões de arquitetura (e por quê)

- **Hash de senha com `pbkdf2_hmac` (stdlib)** — sem dependência nova para hashing; nunca guardamos
  senha em texto puro (exceto o admin do `.env`, que é a escolha explícita do projeto).
- **Token JWT (`pyjwt`)** assinado com `JWT_SECRET` do `.env`, validade configurável.
- **Token em cookie `httpOnly` (`SameSite=Lax`)** definido pelo backend no login. Como o frontend e a
  API são **mesma origem** (o Nuxt faz proxy de `/api/**` para o FastAPI), o cookie é **enviado
  automaticamente** em todas as chamadas `/api/...` existentes — **não é preciso reescrever** as
  chamadas `$fetch`/`fetch` atuais. (Fallback `Authorization: Bearer` também suportado.)
- **Admin único vindo do `.env`** (`LOGIN`/`SENHA`) — não fica no banco. No login, comparamos com o
  `.env`; assim, alterar a senha no `.env` altera o acesso admin na hora.
- **Usuários comuns ficam no banco** (tabela `usuarios`), criados/geridos pelo admin.
- **Autoria por snapshot**: a entidade guarda `criado_por` (nome do criador) + usa o `created_at` já
  existente. Snapshot do nome sobrevive mesmo se o usuário for excluído depois.

> ⚠️ **Segurança é no backend.** O middleware do frontend só faz o *redirect* de UX. Cada rota de
> dados valida o token no servidor (dependência `get_current_user`).

---

## 1. Papéis e fluxo

| Papel | Origem | Acessa |
|---|---|---|
| **admin** | `.env` (`LOGIN`/`SENHA`) | Tudo + `/admin` (gerir usuários) |
| **usuario** | tabela `usuarios` (criado pelo admin) | App principal (dashboard, cadastro, etc.) |

**Recuperação de senha** = o admin abre `/admin`, edita o usuário e define uma nova senha. (Não há
e-mail/auto-serviço — é gerido pelo painel, conforme pedido.)

---

## 2. Ordem de execução (obrigatória)

| # | Arquivo | Entrega | Depende de |
|---|---|---|---|
| 01 | `01-schema-usuarios-e-autoria.md` | Migração: tabela `usuarios` + coluna `criado_por` em `entidades`. | — |
| 02 | `02-backend-auth-core-e-login.md` | `auth.py` (hash, JWT, admin do `.env`, dependências) + rotas `/api/auth/login,me,logout` + **proteger rotas de dados**. | 01 |
| 03 | `03-backend-admin-usuarios.md` | CRUD de usuários `/api/admin/usuarios` (listar/criar/editar/excluir/redefinir senha). | 02 |
| 04 | `04-frontend-login-e-guarda.md` | `composables/useAuth.ts`, `middleware/auth.global.ts`, `pages/login.vue`, botão sair. | 02 |
| 05 | `05-frontend-painel-admin.md` | `pages/admin.vue` (somente admin): UI de gestão de usuários. | 03, 04 |
| 06 | `06-autoria-criador-e-datahora.md` | Gravar `criado_por` no cadastro; exibir nome na lista; clicar → data/hora. | 02 |
| 07 | `07-seguranca-sugestoes-e-aceite.md` | Guardrails, **sugestões de melhoria**, casos de borda e checklist de aceite. | todos |

**Garantia de não quebrar:** após 01, só o banco muda. Após 02, login funciona e as rotas ficam
protegidas (o cookie é enviado automaticamente). Após 04, a tela de login aparece e guarda o app.
05/06 adicionam o painel e a autoria. 07 fecha.

> **Dica de implementação:** ao habilitar a proteção das rotas (passo 02), faça o passo 04 (login no
> front) **logo em seguida**, para não ficar "trancado para fora" durante o desenvolvimento. Em
> ambiente de dev, dá para logar uma vez via `/api/auth/login` (cookie) antes de concluir a UI.

---

## 3. Variáveis de ambiente (`.env`)

Acrescente (mantendo as existentes):
```env
# --- Login / Admin ---
LOGIN=bruno
SENHA=123
JWT_SECRET=troque-por-um-segredo-longo-e-aleatorio
JWT_HORAS=8
```

> Em produção, troque `SENHA` por algo forte e gere um `JWT_SECRET` aleatório longo. Ver sugestões no
> passo 07.

Prossiga para `01-schema-usuarios-e-autoria.md`.
