# Passo 02 — Backend: núcleo de autenticação + login + proteção das rotas

> **Objetivo:** criar `auth.py` (hash de senha, JWT, admin do `.env`, dependências do FastAPI),
> as rotas `/api/auth/login | me | logout`, e **proteger as rotas de dados**.

**Depende de:** 01.
**Arquivos novos:** `auth.py`.
**Arquivos alterados:** `main.py` (imports, modelos, rotas, `Depends` nas rotas existentes),
`requirements.txt` (+`pyjwt`).

---

## 2.1 Dependência

Adicione `pyjwt` ao `requirements.txt` e instale:
```bash
.venv/Scripts/python.exe -m pip install pyjwt
```
> Hashing usa apenas a stdlib (`hashlib.pbkdf2_hmac`) — sem dependência extra.

## 2.2 `auth.py`

```python
# auth.py — hashing (pbkdf2), JWT (pyjwt), admin do .env e dependências do FastAPI.
import os, hmac, hashlib, secrets, base64, datetime
import jwt
from fastapi import Depends, HTTPException, Request
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET", "troque-este-segredo")
ALGO = "HS256"
TOKEN_HORAS = int(os.getenv("JWT_HORAS", "8"))
ADMIN_LOGIN = os.getenv("LOGIN", "bruno")
ADMIN_SENHA = os.getenv("SENHA", "123")


def gerar_hash_senha(senha: str) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt, 200_000)
    return "pbkdf2$" + base64.b64encode(salt).decode() + "$" + base64.b64encode(dk).decode()


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    try:
        _, salt_b64, dk_b64 = hash_armazenado.split("$")
        salt = base64.b64decode(salt_b64)
        esperado = base64.b64decode(dk_b64)
        dk = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt, 200_000)
        return hmac.compare_digest(dk, esperado)
    except Exception:
        return False


def autenticar_admin_env(username: str, senha: str) -> bool:
    return (hmac.compare_digest(username or "", ADMIN_LOGIN)
            and hmac.compare_digest(senha or "", ADMIN_SENHA))


def criar_token(payload: dict) -> str:
    dados = payload.copy()
    dados["exp"] = datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_HORAS)
    return jwt.encode(dados, SECRET_KEY, algorithm=ALGO)


def _ler_token(request: Request) -> str | None:
    token = request.cookies.get("access_token")
    if token:
        return token
    auth = request.headers.get("Authorization", "")
    return auth[7:] if auth.startswith("Bearer ") else None


def get_current_user(request: Request) -> dict:
    token = _ler_token(request)
    if not token:
        raise HTTPException(status_code=401, detail="Não autenticado")
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGO])  # {sub, nome, papel}
    except Exception:
        raise HTTPException(status_code=401, detail="Sessão inválida ou expirada")


def get_current_admin(usuario: dict = Depends(get_current_user)) -> dict:
    if usuario.get("papel") != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito ao administrador")
    return usuario
```

## 2.3 Rotas de autenticação no `main.py`

Imports no topo:
```python
from fastapi import Response, Request
import auth
```
Modelo Pydantic:
```python
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    senha: str = Field(..., min_length=1)
```
Rotas:
```python
@app.post("/api/auth/login")
def login(req: LoginRequest, response: Response):
    # 1) Admin do .env
    if auth.autenticar_admin_env(req.username, req.senha):
        token = auth.criar_token({"sub": req.username, "nome": req.username, "papel": "admin"})
    else:
        # 2) Usuário do banco
        with engine.connect() as conn:
            row = conn.execute(text(
                "SELECT username, nome, senha_hash, ativo FROM usuarios WHERE username = :u"
            ), {"u": req.username}).fetchone()
        if (not row) or (not row.ativo) or (not auth.verificar_senha(req.senha, row.senha_hash)):
            raise HTTPException(status_code=401, detail="Usuário ou senha inválidos.")
        token = auth.criar_token({"sub": row.username, "nome": row.nome, "papel": "usuario"})
        # registra último login (não bloqueia em caso de erro)
        try:
            with engine.begin() as conn:
                conn.execute(text("UPDATE usuarios SET ultimo_login = CURRENT_TIMESTAMP WHERE username = :u"),
                             {"u": req.username})
        except Exception:
            pass

    response.set_cookie("access_token", token, httponly=True, samesite="lax",
                        max_age=auth.TOKEN_HORAS * 3600, path="/")
    return {"ok": True}


@app.get("/api/auth/me")
def me(usuario: dict = Depends(auth.get_current_user)):
    return {"username": usuario["sub"], "nome": usuario.get("nome"), "papel": usuario.get("papel")}


@app.post("/api/auth/logout")
def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    return {"ok": True}
```

> **Cookie + proxy:** o Nuxt faz proxy de `/api/**` → FastAPI (mesma origem para o browser), então o
> cookie `httpOnly` é enviado sozinho nas chamadas seguintes. Verifique no passo 04. Caso o proxy não
> repasse o cookie no seu ambiente, use o fallback `Authorization: Bearer` (o `auth.py` já aceita).

## 2.4 Proteger as rotas de dados existentes

Adicione `usuario: dict = Depends(auth.get_current_user)` à assinatura das rotas que manipulam dados.
No mínimo, proteja as de **escrita** e, idealmente, as de **leitura** também (app interno):

- `create_entidade`, `update_entidade`, `delete_entidade`
- `create_repasse_individual`
- exports: `export_geral` (se ainda existir), `export_entidade`, `export_dados`
- import: `importar_planilha`, `baixar_modelo_importacao`
- chat: `chat` (e upload de excel)
- leituras: `get_entidades`, `get_entidade_completa`, `get_*` de repasses

Exemplo:
```python
@app.post("/api/entidades", status_code=status.HTTP_201_CREATED)
def create_entidade(entidade: EntidadeCreate, usuario: dict = Depends(auth.get_current_user)):
    ...
```
> **Não** proteja `/api/auth/login` nem `/api/auth/me` (esta já exige token por dependência) nem o
> health check `GET /`. O `usuario` injetado será usado também no passo 06 (autoria).

---

## 2.5 Critérios de aceite

- [ ] `POST /api/auth/login` com `LOGIN`/`SENHA` do `.env` → `200`, define cookie, `papel=admin`.
- [ ] Login com usuário do banco válido → `200`, `papel=usuario`; senha errada → `401`.
- [ ] `GET /api/auth/me` sem cookie → `401`; com cookie → dados do usuário.
- [ ] Uma rota de dados protegida sem login → `401`.
- [ ] Alterar `SENHA` no `.env` e reiniciar → o login admin passa a exigir a nova senha.

## 2.6 Segurança / reversão

- Senhas do banco com `pbkdf2` (200k iterações) + comparação `compare_digest`.
- Reverter = remover as rotas/imports e os `Depends`, e apagar `auth.py`.

> Próximo: `03-backend-admin-usuarios.md`.
