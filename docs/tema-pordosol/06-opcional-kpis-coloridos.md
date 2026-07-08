# Passo 06 — (Opcional) KPIs totalmente coloridos (Faixa B)

> **Objetivo:** deixar os 3 cartões de KPI **inteiros coloridos** (gradiente + texto branco), igual
> ao mockup, em vez de só a faixa no topo do passo 04. Exige **edição mínima de markup** (adicionar
> uma classe a cada cartão) em `components/EntitySelector.vue`.

**Arquivos alterados:** `components/EntitySelector.vue` (3 linhas) + `assets/css/main.css` (bloco do tema).
**Risco:** médio (mexe em markup, mas só adiciona classes — não altera lógica).

> Se preferir o visual mais sóbrio (cartões brancos com faixa de cor), **pule este passo** — o passo
> 04 já entrega um resultado bonito e 100% sem markup.

---

## 6.1 Markup — adicionar 1 classe a cada cartão

No `EntitySelector.vue`, no bloco `<div class="kpi-grid">`, cada cartão começa com
`class="kpi-card"`. Adicione as classes de cor:

| Cartão | Antes | Depois |
|---|---|---|
| 1 — Total | `class="kpi-card"` | `class="kpi-card kpi-sun kpi-sun-teal"` |
| 2 — Ativas | `class="kpi-card"` | `class="kpi-card kpi-sun kpi-sun-gold"` |
| 3 — Volume | `class="kpi-card"` | `class="kpi-card kpi-sun kpi-sun-red"` |

> Mantenha o `:class="{ 'active-filter': ... }"` e os `@click` existentes — só acrescente as classes
> no atributo `class` estático. Não remova os `style="..."` inline; o CSS abaixo cuida deles.

## 6.2 CSS (acrescentar ao bloco do tema, depois das regras de KPI do passo 04)

```css
/* ── KPIs coloridos (Faixa B) ── */
.kpi-sun{ border:none; }
.kpi-sun::before{ display:none; }                 /* dispensa a faixa do passo 04 */
.kpi-sun:hover{ transform:translateY(-2px); box-shadow:0 14px 30px rgba(150,80,20,.20); }
.kpi-sun .kpi-value, .kpi-sun .kpi-label, .kpi-sun .kpi-sub{ color:#fff; }
.kpi-sun .kpi-icon-box{ background:rgba(255,255,255,.22) !important; }   /* vence o style inline */
.kpi-sun .kpi-icon-box svg{ stroke:#fff; }        /* o stroke inline é atributo: CSS vence sem !important */
.kpi-sun .kpi-trend{ background:rgba(255,255,255,.22); color:#fff; }

.kpi-sun-teal{ background:linear-gradient(135deg,var(--pds-azul),var(--pds-azul-esc)); }
.kpi-sun-red { background:linear-gradient(135deg,var(--pds-vermelho),var(--pds-maroon)); }
.kpi-sun-gold{ background:linear-gradient(135deg,var(--pds-ouro),var(--pds-laranja)); }
/* o cartão ouro pede texto escuro para legibilidade */
.kpi-sun-gold .kpi-value, .kpi-sun-gold .kpi-label, .kpi-sun-gold .kpi-sub{ color:#3A2400; }
.kpi-sun-gold .kpi-icon-box svg{ stroke:#3A2400; }
.kpi-sun-gold .kpi-trend{ background:rgba(0,0,0,.12); color:#3A2400; }
```

> **Por que funciona:**
> - O fundo do ícone é `style="background:#eff6ff"` (estilo inline) → precisa de `!important`.
> - O `stroke="#1d4ed8"` do SVG é **atributo de apresentação** → CSS comum já vence (sem `!important`).
> - `.active-filter::after` (passo 04) continua funcionando como destaque do filtro selecionado.

---

## 6.3 Critérios de aceite

- [ ] Os 3 KPIs ficam coloridos por inteiro: Total (teal), Ativas (ouro→laranja), Volume (vermelho).
- [ ] Números e rótulos legíveis (branco nos escuros, marrom no ouro); ícones acompanham.
- [ ] Clicar nos cartões/filtro continua funcionando (lógica intacta).

## 6.4 Reversão

Remova as 3 classes adicionadas no `EntitySelector.vue` e esta subseção do bloco do tema. (Sem o
passo 06, o passo 04 mantém os cartões brancos com faixa de cor.)

> Próximo: `07-verificacao-e-reversao.md`.
