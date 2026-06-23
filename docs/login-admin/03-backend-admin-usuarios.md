# Passo 03 — Backend: CRUD de usuários (somente admin)

> **Objetivo:** endpoints que o painel `/admin` usa para **listar, criar, editar, excluir** usuários
> e **redefinir senha** (a "recuperação"). Todos exigem o admin do `.env` (`get_current_admin`).

**Depende de:** 02.
**Arquivos alterados:** `main.py` (modelos + 4 rotas).

---

## 3.1 Modelos Pydantic

```python
class UsuarioCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=80)
    nome: str = Field(..., min_length=1, max_length=160)
    senha: str = Field(..., min_length=4)
    ativo: bool = True

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    senha: Optional[str] = None     # se vier preenchida, redefine a senha (recuperação)
    ativo: Optional[bool] = None
```

## 3.2 Rotas (todas com `Depends(auth.get_current_admin)`)

```python
@app.get("/api/admin/usuarios")
def listar_usuarios(admin: dict = Depends(auth.get_current_admin)):
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT id, username, nome, ativo, criado_em, ultimo_login
            FROM usuarios ORDER BY nome
        """)).fetchall()
    return [{
        "id": str(r.id), "username": r.username, "nome": r.nome, "ativo": r.ativo,
        "criado_em": r.criado_em.isoformat() if r.criado_em else None,
        "ultimo_login": r.ultimo_login.isoformat() if r.ultimo_login else None,
    } for r in rows]


@app.post("/api/admin/usuarios", status_code=status.HTTP_201_CREATED)
def criar_usuario(req: UsuarioCreate, admin: dict = Depends(auth.get_current_admin)):
    if req.username.strip().lower() == auth.ADMIN_LOGIN.lower():
        raise HTTPException(status_code=400, detail="Esse nome de usuário é reservado ao administrador.")
    senha_hash = auth.gerar_hash_senha(req.senha)
    try:
        with engine.begin() as conn:
            row = conn.execute(text("""
                INSERT INTO usuarios (username, nome, senha_hash, ativo)
                VALUES (:u, :n, :h, :a) RETURNING id
            """), {"u": req.username.strip(), "n": req.nome.strip(), "h": senha_hash, "a": req.ativo}).fetchone()
        return {"id": str(row.id), "ok": True}
    except SQLAlchemyError as e:
        if "unique" in str(e).lower():
            raise HTTPException(status_code=409, detail="Já existe um usuário com esse username.")
        raise HTTPException(status_code=500, detail="Erro ao criar usuário.")


@app.put("/api/admin/usuarios/{user_id}")
def atualizar_usuario(user_id: str, req: UsuarioUpdate, admin: dict = Depends(auth.get_current_admin)):
    campos, params = [], {"id": user_id}
    if req.nome is not None:
        campos.append("nome = :n"); params["n"] = req.nome.strip()
    if req.ativo is not None:
        campos.append("ativo = :a"); params["a"] = req.ativo
    if req.senha:  # redefinição de senha (recuperação)
        campos.append("senha_hash = :h"); params["h"] = auth.gerar_hash_senha(req.senha)
    if not campos:
        return {"ok": True}  # nada a alterar
    with engine.begin() as conn:
        res = conn.execute(text(f"UPDATE usuarios SET {', '.join(campos)} WHERE id = :id"), params)
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return {"ok": True}


@app.delete("/api/admin/usuarios/{user_id}")
def excluir_usuario(user_id: str, admin: dict = Depends(auth.get_current_admin)):
    with engine.begin() as conn:
        res = conn.execute(text("DELETE FROM usuarios WHERE id = :id"), {"id": user_id})
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return {"ok": True}
```

> **Recuperação de senha = redefinição pelo admin:** ao editar um usuário e preencher o campo
> `senha`, o hash é regravado. É exatamente o "sistema de recuperação gerido pelo painel admin".
>
> **Dica (passo 07):** preferir **desativar** (`ativo = false`) em vez de excluir, para preservar o
> histórico/autoria. A exclusão continua disponível para quando for realmente necessário.

---

## 3.3 Critérios de aceite

- [ ] Sem ser admin (usuário comum), chamar `/api/admin/usuarios` → `403`.
- [ ] Como admin: criar usuário → aparece na listagem; username duplicado → `409`.
- [ ] Editar nome/ativo funciona; preencher `senha` redefine (o usuário passa a logar com a nova).
- [ ] Excluir remove o usuário; usuário inexistente → `404`.
- [ ] Não é possível criar usuário com o mesmo username do admin do `.env`.

## 3.4 Segurança / reversão

Todas as rotas exigem admin. Senhas sempre hasheadas. Reverter = remover as 4 rotas e os 2 modelos.

> Próximo: `04-frontend-login-e-guarda.md`.
