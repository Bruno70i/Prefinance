# Plano — Aplicar o tema "Marítimo · Pôr do Sol" no app Nuxt/Vue

> **Objetivo:** dar ao PreFinance o visual do mockup `mockups-ui/02a-maritimo-pordosol.html`
> (sidebar navy com brilho quente, topbar em degradê laranja→vermelho→ouro, KPIs coloridos, acentos
> laranja/ouro, fundo quente) **sem quebrar o frontend nem o backend**.
>
> **Para quem vai implementar (IA/dev):** leia este índice antes de começar. A estratégia foi
> escolhida para ser **reversível e de baixo risco**.

---

## 0. Estratégia (por que é seguro)

O `assets/css/main.css` (169 linhas) usa **cores fixas (azul), sem variáveis**. Os componentes
(`pages/index.vue`, `components/EntitySelector.vue`, etc.) usam **classes globais** desse arquivo
(`.sidebar`, `.top-bar`, `.kpi-card`, `.btn-primary`, `.filter-pill`, `.badge`, …).

➡️ **Não vamos reescrever o `main.css` nem o markup.** Vamos **acrescentar um único bloco de tema
no FINAL do `main.css`**, delimitado por comentários:

```css
/* ====================== TEMA PÔR DO SOL — INÍCIO ====================== */
   ... overrides ...
/* ======================  TEMA PÔR DO SOL — FIM  ====================== */
```

Como o CSS aplica, em igualdade de especificidade, a **última regra declarada**, esse bloco
re-skina o app inteiro. **Reverter = apagar o bloco** (e a linha de fonte no `nuxt.config.ts`).
Nenhuma lógica de Vue, nenhuma rota e nenhum endpoint são tocados.

### Faixas de entrega
- **Faixa A (passos 01–05): só CSS, zero risco de markup.** Re-skina sidebar, topbar, fundo, busca,
  KPIs (com faixa de cor no topo), tabela, pills, paginação, botões, inputs e acentos, sem tocar em
  nenhum `.vue`.
- **Faixa B (passos 06 e 08): pequenos ajustes pontuais de markup/estilo** — KPIs **totalmente
  coloridos** (`EntitySelector.vue`) e os componentes com estilo inline próprio (**chat, login,
  admin**).

> 🎯 **Para ficar EXATAMENTE igual ao `02a-maritimo-pordosol.html`, faça TODOS os passos (01–06 e
> 08).** Os passos 06 e 08 não são dispensáveis nesse caso — são eles que colorem os KPIs por
> inteiro e aquecem o chat/login/admin, que têm `style="..."` próprio e não pegam o tema sozinhos.
> Se quiser uma versão mais sóbria, pode parar no passo 05.

> ⚠️ **Estilos inline vencem o CSS.** O fundo dos ícones dos KPIs e os componentes chat/login/admin
> usam `style="..."`/`<style scoped>` próprios. O passo 06 trata os KPIs e o passo 08 trata
> chat/login/admin — com as substituições exatas (find → replace).

---

## 1. Paleta (extraída do mockup 02a)

| Token | Hex | Uso |
|---|---|---|
| Fundo quente | `#F3F0EC` | `body` |
| Navy (sidebar) | `#14304F` → `#0A1B30` | degradê da sidebar |
| Ouro | `#FBBE12` | acento principal, ativo |
| Laranja | `#F5791E` (claro `#FF9A3D`) | acento/CTA |
| Vermelho | `#E0241F` (maroon `#8C1410`) | topbar, KPI, excluir |
| Teal | `#13A0B0` → `#0A6E7E` | KPI "Total" (toque frio) |
| Creme | `#FFE7CF` / texto `#A23410` | botão na topbar quente |

---

## 2. Ordem de execução

| # | Arquivo | Entrega | Risco |
|---|---|---|---|
| 01 | `01-base-fonte-e-fundo.md` | Cria o bloco de tema + tokens `:root`, fundo quente e fonte (Plus Jakarta Sans). | baixo |
| 02 | `02-sidebar.md` | Sidebar navy com brilho quente, nav ativa em ouro/laranja. | baixo |
| 03 | `03-topbar-e-busca.md` | Topbar em degradê quente + botão creme; foco da busca em laranja. | baixo |
| 04 | `04-kpis-tabela-pills.md` | KPIs com faixa de cor (teal/ouro/vermelho), hover/pills/paginação quentes. | baixo |
| 05 | `05-botoes-inputs-acentos.md` | Botões, foco de inputs, context-badge, steps, drop-zone em tons quentes. | baixo |
| 06 | `06-opcional-kpis-coloridos.md` | KPIs totalmente coloridos — 3 classes em `EntitySelector.vue`. **(Necessário p/ ficar igual ao 02a.)** | médio |
| 07 | `07-verificacao-e-reversao.md` | Checklist por tela + como reverter 100%. | — |
| 08 | `08-componentes-inline-chat-login-admin.md` | Aquece chat, login e admin (estilo inline). **(Necessário p/ ficar igual ao 02a.)** | baixo |

**Garantia:** após cada passo, o app continua funcionando — só muda a aparência. Recomenda-se
recarregar o `npm run dev` e conferir o dashboard a cada passo.

---

## 3. Convenções

- Todo CSS dos passos 01–05 vai **dentro do mesmo bloco** `TEMA PÔR DO SOL` (apenas concatene as
  subseções, na ordem dos passos).
- **Não** remova nem edite regras existentes do `main.css` — só **acrescente** ao final.
- Mantenha o **DM Mono** para campos mono (`.cb-value`, `.search-kbd`) — só o texto geral troca de
  fonte.
- Cores **semânticas** (badge verde = ativa, vermelho = excluir, verde = "Efetivar") são
  preservadas por padrão; há uma observação opcional para aquecê-las.

Prossiga para `01-base-fonte-e-fundo.md`.
