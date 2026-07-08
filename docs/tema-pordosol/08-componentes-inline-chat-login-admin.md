# Passo 08 — Componentes com estilo inline (chat, login, admin)

> **Objetivo:** aquecer os componentes que **não** usam as classes globais do `main.css` e por isso
> não pegam o tema sozinhos — o botão/painel do **Assistente IA**, a **tela de login** e o **painel
> admin** — para o app ficar **inteiro** no estilo "Pôr do Sol", igual ao mockup `02a`.
>
> São **substituições pontuais de cor** (find → replace) nos `<style scoped>` de cada arquivo.
> Nenhuma lógica muda.

**Arquivos alterados:** `components/AssistenteIA.vue`, `pages/login.vue`, `pages/admin.vue`.

---

## 8.1 `components/AssistenteIA.vue`

Substitua **exatamente** estas ocorrências (azul → quente):

| Onde (seletor) | Trocar isto | Por isto |
|---|---|---|
| `.ia-fab` → `background:` | `linear-gradient(135deg, #0b5394, #073763)` | `linear-gradient(135deg, #F5791E, #FBBE12)` |
| `.ia-fab` → `color:` | `color: #fff;` | `color: #3A2400;` |
| `.ia-fab` → `box-shadow:` | `0 8px 25px rgba(11, 83, 148, 0.4)` | `0 8px 25px rgba(245, 121, 30, 0.5)` |
| `.ia-fab:hover` → `box-shadow:` | `0 12px 30px rgba(11, 83, 148, 0.5)` | `0 12px 30px rgba(245, 121, 30, 0.55)` |
| `.ia-fab:hover` → `background:` | `linear-gradient(135deg, #0d6efd, #0b5394)` | `linear-gradient(135deg, #E0241F, #F5791E)` |
| `.ia-header` → `background:` | `linear-gradient(135deg, #0b5394, #073763)` | `linear-gradient(100deg, #F5791E 0%, #E0241F 65%, #FBBE12 130%)` |
| `.loading-pulse` → `background:` | `background: #f0f7ff;` | `background: #FFF6E6;` |
| `.loading-pulse` → `border-left-color:` | `border-left-color: #3b82f6;` | `border-left-color: #F5791E;` |
| `.loading-pulse` → `color:` | `color: #1d4ed8;` | `color: #A23410;` |
| `.ia-msg.user .ia-bubble` → `background:` | `background: #0b5394;` | `background: linear-gradient(135deg, #F5791E, #E0241F);` |
| `.ia-btn-attach:hover` → `color:` | `color: #0b5394;` | `color: #A23410;` |
| `.ia-input-field:focus` → `border-color:` | `border-color: #0b5394;` | `border-color: #F5791E;` |
| `.ia-btn-send` → `background:` | `background: #0b5394;` | `background: linear-gradient(135deg, #F5791E, #E0241F);` |

> Resultado: o botão flutuante "💬 Assistente IA" fica laranja→ouro (texto escuro), e o cabeçalho do
> chat ganha o mesmo degradê quente da topbar — igual ao espírito do `02a`.

## 8.2 `pages/login.vue`

| Onde (seletor) | Trocar isto | Por isto |
|---|---|---|
| `.logo-box` → `background:` | `linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)` | `linear-gradient(135deg, #F5791E 0%, #E0241F 100%)` |
| `.input-wrapper input:focus` → `border-color:` | `border-color: #3b82f6;` | `border-color: #F5791E;` |
| `.input-wrapper input:focus` → `box-shadow:` | `0 0 0 3px rgba(59, 130, 246, 0.15)` | `0 0 0 3px rgba(245, 121, 30, 0.18)` |
| `.input-wrapper input:focus + .input-icon` → `color:` | `color: #3b82f6;` | `color: #F5791E;` |
| `.btn-submit` → `background:` | `linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)` | `linear-gradient(135deg, #F5791E 0%, #E0241F 100%)` |
| `.btn-submit` → `box-shadow:` | `0 4px 12px rgba(29, 78, 216, 0.2)` | `0 4px 12px rgba(245, 121, 30, 0.3)` |
| `.btn-submit:hover` → `background:` | `linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%)` | `linear-gradient(135deg, #E0241F 0%, #FBBE12 100%)` |
| `.btn-submit:hover` → `box-shadow:` | `0 6px 16px rgba(59, 130, 246, 0.35)` | `0 6px 16px rgba(245, 121, 30, 0.4)` |

> A tela de login mantém a base escura, mas com a logo e o botão em laranja→vermelho e o foco dos
> campos em laranja.

## 8.3 `pages/admin.vue`

| Onde | Trocar isto | Por isto |
|---|---|---|
| Eyebrow "Área Administrativa" (inline, ~linha 6) | `color: #3b82f6;` | `color: #F5791E;` |
| `.inp:focus` → `border-color:` | `border-color: #3b82f6;` | `border-color: #F5791E;` |
| `.inp:focus` → `box-shadow:` | `0 0 0 3px rgba(59, 130, 246, 0.1)` | `0 0 0 3px rgba(245, 121, 30, 0.12)` |

> Os botões do admin usam as classes `.btn-*` globais → já herdam o tema dos passos 01–05. Só esses
> 3 pontos de azul inline precisam de ajuste.

---

## 8.4 Critérios de aceite

- [ ] O botão flutuante do Assistente IA fica laranja→ouro; o cabeçalho do chat em degradê quente.
- [ ] Balão de mensagem do usuário e botão "Enviar" do chat em laranja/vermelho.
- [ ] Login: logo e botão "Entrar" em tons quentes; foco dos campos laranja.
- [ ] Admin: eyebrow e foco dos campos em laranja; botões já quentes pelos passos anteriores.
- [ ] Tudo continua funcionando (chat, login, CRUD de usuários).

## 8.5 Reversão

Reverta cada substituição para o valor azul original (a coluna "Trocar isto"). Como são edições
pontuais e isoladas, dá para reverter arquivo por arquivo.

> Fim. Com os passos 01–06 + 08 aplicados, o app fica **inteiro** no estilo `02a-maritimo-pordosol`.
> Volte ao `00-INDICE-E-ORDEM.md`.
