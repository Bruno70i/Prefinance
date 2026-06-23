# Passo 07 — Segurança, sugestões de melhoria e aceite final

> **Objetivo:** consolidar as proteções, listar **melhorias recomendadas** (você pediu ideias) e dar
> o checklist final de validação fim a fim.

**Depende de:** todos os passos anteriores.

---

## 7.1 Segurança (o que já está garantido e o que reforçar)

1. **O backend é a fronteira.** Toda rota de dados exige `Depends(get_current_user)`; o middleware do
   frontend é só UX. Confirme que **nenhuma** rota sensível ficou sem proteção (passo 02 §2.4).
2. **Senhas hasheadas** com `pbkdf2_hmac` (200k iterações) + `compare_digest`. Nunca em texto puro
   (exceto o admin do `.env`, por decisão do projeto).
3. **Segredo do JWT:** defina `JWT_SECRET` longo e aleatório no `.env` (não use o valor padrão).
4. **Troque a senha do admin** em produção (`SENHA=123` é só para desenvolvimento).
5. **Cookie:** em produção sob HTTPS, adicione `secure=True` ao `set_cookie`. Mantenha
   `httponly=True` e `samesite="lax"`.
6. **Expiração de sessão:** o token expira em `JWT_HORAS`. No front, trate `401` global redirecionando
   para `/login` (auto-logout) — ver sugestão 7.2.7.
7. **Não logar segredos:** garanta que senhas/tokens não apareçam em `print`/logs.

## 7.2 Sugestões de melhoria (ideias extras)

> Opcionais, em ordem de valor. Implemente conforme a necessidade.

1. **Desativar em vez de excluir usuário.** Já existe o campo `ativo`; prefira desativar para
   preservar histórico e a coluna `criado_por`. Mantenha o excluir só para casos reais.
2. **Rastrear edição (`atualizado_por` / `updated_at`).** A coluna `atualizado_por` já foi sugerida no
   passo 01; preencha no `update_entidade` e mostre na lista (tooltip "editado por X em ...").
3. **Log de auditoria.** Tabela `auditoria(id, usuario, acao, entidade_id, detalhe, em)` registrando
   criação/edição/exclusão. Excelente para um órgão público (rastreabilidade).
4. **Papéis além de admin.** Ex.: `gestor` (cria/edita) e `leitura` (só consulta). Hoje há
   `admin`/`usuario`; dá para evoluir o campo `papel` e checar nas rotas.
5. **Política de senha.** Exigir mínimo de 8 caracteres e/ou complexidade ao criar/redefinir.
6. **Bloqueio por tentativas.** Após N falhas de login, atrasar/bloquear temporariamente (anti força
   bruta). Pode ser simples (contador em memória/Redis) ou via tabela.
7. **Auto-logout no `401`.** Um wrapper de `$fetch` (`onResponseError`) que, ao receber `401`, limpa o
   estado e manda para `/login`. Melhora a UX quando o token expira.
8. **Promover usuário a admin.** Hoje o admin é único (do `.env`). Futuro: um campo `papel='admin'` no
   banco para ter mais de um administrador, mantendo o do `.env` como "super-admin" de resgate.
9. **"Minhas parcerias".** Filtro no dashboard por `criado_por = usuário logado`.
10. **Forçar troca no 1º acesso.** Flag `precisa_trocar_senha` para senhas definidas pelo admin.
11. **Avatar/iniciais** do criador na lista (ex.: círculo com "BR") em vez de só o texto.

## 7.3 Casos de borda

| Situação | Comportamento |
|---|---|
| Token expirado | Rotas → `401`; front redireciona para `/login`. |
| Admin muda `SENHA` no `.env` | Após reiniciar o backend, o login admin exige a nova senha; tokens antigos seguem válidos até expirar (aceitável) — para invalidar na hora, troque também `JWT_SECRET`. |
| Excluir usuário que criou parcerias | As parcerias mantêm o nome em `criado_por` (snapshot). |
| Username do admin tentado no cadastro | Bloqueado (passo 03). |
| Usuário inativo tenta logar | `401` (backend checa `ativo`). |
| Proxy não repassa cookie | Usar fallback `Authorization: Bearer` (passo 04 §4.6). |

## 7.4 Checklist de aceite (fim a fim)

**Login**
- [ ] Sem login, qualquer rota redireciona para `/login`; backend recusa as APIs com `401`.
- [ ] Login com `LOGIN`/`SENHA` do `.env` entra como **admin**.
- [ ] Login com usuário do banco entra como **usuario**; senha errada → erro.
- [ ] "Sair" encerra a sessão.

**Admin `/admin`**
- [ ] Só o admin acessa; usuário comum é redirecionado.
- [ ] Criar, editar, excluir usuários funciona; username duplicado é barrado.
- [ ] **Redefinir senha** pelo painel funciona (usuário passa a logar com a nova).
- [ ] Desativar um usuário impede o login dele.

**Autoria**
- [ ] Nova parceria registra `criado_por` = nome de quem está logado.
- [ ] Na lista, o nome do criador aparece; clicar mostra data e hora.

**Segurança / não-regressão**
- [ ] Senhas no banco estão hasheadas (confira a coluna `senha_hash`).
- [ ] Alterar `.env` (SENHA) muda o acesso admin após reiniciar.
- [ ] Exportação, importação, edição, chat e dashboard seguem funcionando logado.

## 7.5 Teste manual sugerido

1. Suba backend e frontend; tente abrir `/` → deve ir para `/login`.
2. Entre como admin (`.env`), abra `/admin`, crie o usuário "Maria".
3. Saia, entre como "Maria", crie uma parceria → confira "Maria" na coluna "Criado por" e a data/hora.
4. Volte como admin, redefina a senha de "Maria" e confirme o novo login.
5. Desative "Maria" e confirme que o login dela é recusado.

---

## 7.6 Resumo dos artefatos

| Arquivo | Papel |
|---|---|
| `migrations/2026_login.sql` | Tabela `usuarios` + coluna `criado_por` |
| `auth.py` | Hash, JWT, admin do `.env`, dependências de proteção |
| `main.py` (alterado) | Rotas `/api/auth/*`, CRUD `/api/admin/usuarios`, `Depends` nas rotas de dados, autoria no INSERT/SELECT |
| `composables/useAuth.ts` | Estado de sessão (login/logout/me) |
| `middleware/auth.global.ts` | Guarda de rotas (login e `/admin`) |
| `pages/login.vue` | Tela de login |
| `pages/admin.vue` | Painel de gestão de usuários |
| `components/EntitySelector.vue` (alterado) | Coluna "Criado por" + clique → data/hora |
| `composables/useEntity.ts` (alterado) | Campos `criado_por`/`created_at` |
| `requirements.txt` (alterado) | +`pyjwt` |

> Fim do plano. Volte ao `00-INDICE-E-ORDEM.md` para a visão geral.
