# Como hospedar o PreFinance na rede local (acesso simultâneo da equipe)

> Objetivo: rodar o sistema em **um computador (o "servidor")** e deixar que **todos os outros
> computadores da equipe acessem ao mesmo tempo**, pelo navegador, dentro da mesma rede (Wi-Fi/cabo).

---

## 1. Como funciona (a ideia)

```
   Outros PCs da equipe  ──►  http://192.168.1.50:3000  ──►  [ PC SERVIDOR ]
   (navegador)                                                ├─ Nuxt (porta 3000)  ──► /api ──► FastAPI (porta 8000)
                                                              ├─ FastAPI (porta 8000, local)
                                                              ├─ PostgreSQL (banco)
                                                              └─ Ollama (Assistente IA, local)
```

- Só **um** PC roda tudo (backend, frontend, banco e a IA).
- Os demais só abrem o navegador e digitam o endereço do servidor.
- **Detalhe importante:** o frontend (Nuxt) já encaminha `/api` para o FastAPI **dentro do próprio
  servidor**. Por isso, **você só precisa expor a porta do frontend (3000)** na rede — o backend
  (8000) pode continuar só local.
- **Acesso simultâneo:** sim, vários usuários ao mesmo tempo. Os dados ficam no PostgreSQL (não em
  memória), então o uso concorrente é seguro.

---

## 2. No PC servidor, deixe instalado

- **PostgreSQL** (o banco que você já usa) — com os dados do projeto.
- **Python + venv** do projeto (com `requirements.txt` instalado).
- **Node.js** (para rodar o Nuxt).
- **Ollama** + o modelo (`llama3.1:8b`) — só se quiser o Assistente IA funcionando para todos.
- O projeto **PreFinance** copiado para uma pasta (ex.: `D:\github\Prefinance`).

> Escolha o PC mais estável e que fique **ligado** durante o expediente.

---

## 3. Passo a passo

### 3.1 Dê um IP fixo ao servidor
Para o endereço não mudar toda vez que liga o PC:
- **Melhor opção:** no roteador, faça uma **reserva de DHCP** pelo MAC do PC servidor (ele sempre
  recebe, por ex., `192.168.1.50`).
- Alternativa: configurar IP estático no Windows (Configurações → Rede → IP manual).

Para descobrir o IP atual, no servidor abra o terminal e rode:
```bat
ipconfig
```
Anote o **Endereço IPv4** (ex.: `192.168.1.50`).

### 3.2 Gere a versão de produção do frontend (uma vez)
Na pasta do projeto, no servidor:
```bat
npm install
npm run build
```
Isso cria a pasta `.output` (site otimizado, mais rápido e estável que o modo de desenvolvimento).

### 3.3 Rode os serviços expondo na rede
Crie um arquivo **`iniciar-rede.bat`** na raiz do projeto (baseado no seu `iniciar.bat`):

```bat
@echo off
title PreFinance - Servidor de Rede

echo [+] Iniciando Backend (FastAPI, local na porta 8000)...
start "Backend" cmd /k "cd /d %~dp0 && .venv\Scripts\activate.bat && python main.py"

timeout /t 3 /nobreak > NUL

echo [+] Iniciando Frontend (Nuxt producao, exposto na rede na porta 3000)...
start "Frontend" cmd /k "cd /d %~dp0 && set HOST=0.0.0.0&& set PORT=3000&& node .output/server/index.mjs"

echo.
echo Servidor no ar! A equipe acessa por: http://SEU_IP:3000
timeout /t 6
```

- `HOST=0.0.0.0` faz o Nuxt **aceitar conexões da rede** (não só do próprio PC).
- O backend continua em `localhost:8000` (não precisa expor).

> **Atalho rápido (sem build):** se quiser testar antes, dá para rodar em modo dev exposto:
> troque a linha do frontend por `npm run dev -- --host 0.0.0.0`. Funciona, mas o modo de
> **produção (`node .output/...`) é mais rápido e estável** para o dia a dia.

### 3.4 Libere a porta no Firewall do Windows
No servidor, abra o **PowerShell como Administrador** e rode:
```powershell
New-NetFirewallRule -DisplayName "PreFinance 3000" -Direction Inbound -Protocol TCP -LocalPort 3000 -Action Allow
```
(Isso permite que os outros PCs alcancem a porta 3000.)

### 3.5 A equipe acessa
Em qualquer PC da mesma rede, no navegador:
```
http://192.168.1.50:3000
```
(troque pelo IP do seu servidor). Pronto — fazem login e usam normalmente.

---

## 4. Iniciar sozinho quando ligar o PC (opcional, recomendado)

Para não precisar abrir o `.bat` manualmente:

- **Opção simples:** coloque um atalho do `iniciar-rede.bat` na pasta
  `shell:startup` (Win+R → digite `shell:startup` → cole o atalho). Ele roda no login do Windows.
- **Opção robusta (roda como serviço, reinicia se cair):** use o **NSSM** (Non-Sucking Service
  Manager) para registrar o backend e o frontend como serviços do Windows. Assim sobem com o PC,
  mesmo sem ninguém logado, e reiniciam sozinhos em caso de falha.

> Lembre de desativar a **suspensão/hibernação** do servidor para ele não "dormir" no meio do
> expediente (Configurações → Energia).

---

## 5. Desempenho e usuários simultâneos

- Para uma equipe pequena (tipicamente 3–15 pessoas), **um PC comum dá conta tranquilo**.
- O `python main.py` usa 1 processo (uvicorn). Se notar lentidão com muita gente ao mesmo tempo,
  dá para rodar com mais "workers":
  ```bat
  .venv\Scripts\activate.bat && uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4
  ```
  (4 processos atendendo em paralelo.)
- O **Assistente IA (Ollama)** é o que mais pesa: ele responde **uma pergunta por vez** e usa CPU/GPU.
  Para vários usuários simultâneos no chat, prefira um PC com boa memória/GPU — ou avise a equipe que
  o chat pode enfileirar respostas em horários de pico.

---

## 6. Backup do banco (não pule isto)

Os dados ficam no PostgreSQL do servidor. Faça backup periódico:
```bat
pg_dump -U postgres -d prefinance -f D:\backups\prefinance_%date%.sql
```
Agende isso no **Agendador de Tarefas** do Windows (ex.: todo dia às 19h). Guarde uma cópia em outro
lugar (pendrive/nuvem) de tempos em tempos.

---

## 7. Segurança na rede local

- O acesso é por **HTTP** (sem cadeado). Em rede interna e confiável, é aceitável. Como o login
  trafega sem criptografia, **não reutilize senhas importantes** nos usuários.
- **Troque a senha do admin** no `.env` (`SENHA=123` é só para teste) e gere um `JWT_SECRET` forte.
- (Opcional, para criptografar) é possível pôr um **HTTPS** com um proxy reverso (ex.: **Caddy**) e
  um certificado local — mas para uso interno não é obrigatório.
- Mantenha o PostgreSQL aceitando conexões **só do próprio servidor** (padrão) — ninguém de fora
  fala direto com o banco.

---

## 8. Checklist rápido

- [ ] PC servidor com IP fixo (ex.: `192.168.1.50`) e que fica ligado.
- [ ] PostgreSQL, Python(venv), Node e (opcional) Ollama instalados nele.
- [ ] `npm run build` rodado uma vez.
- [ ] `iniciar-rede.bat` sobe backend (local) + frontend (`HOST=0.0.0.0`, porta 3000).
- [ ] Regra de firewall liberando a porta 3000.
- [ ] Equipe acessa `http://IP-DO-SERVIDOR:3000` e faz login.
- [ ] Auto-start configurado + backup do banco agendado.
- [ ] Senha do admin trocada.
