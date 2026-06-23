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
        # Use UTC timestamp parsing and allow validation
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGO])  # {sub, nome, papel}
    except Exception:
        raise HTTPException(status_code=401, detail="Sessão inválida ou expirada")


def get_current_admin(usuario: dict = Depends(get_current_user)) -> dict:
    if usuario.get("papel") != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito ao administrador")
    return usuario
