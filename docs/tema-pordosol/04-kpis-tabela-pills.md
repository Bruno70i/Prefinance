# Passo 04 — KPIs, tabela, pills e paginação

> **Objetivo:** dar cor aos cartões de KPI (faixa teal/ouro/vermelho no topo, como o mockup) e
> aquecer hover da tabela, filtros (pills) e paginação. **Faixa A: só CSS.** (Os cartões totalmente
> coloridos ficam no passo 06, opcional.)

**Arquivos alterados:** `assets/css/main.css` (bloco do tema).

---

## 4.1 CSS (acrescentar ao bloco do tema)

```css
/* ── KPI cards: faixa de cor no topo (teal / ouro→laranja / vermelho→maroon) ── */
.kpi-grid{ grid-template-columns:repeat(3,1fr); }  /* 3 cartões reais ocupam a linha toda */
.kpi-grid .kpi-card::before{
  content:""; position:absolute; top:0; left:0; right:0; height:4px; border-radius:12px 12px 0 0;
}
.kpi-grid .kpi-card:nth-child(1)::before{ background:linear-gradient(90deg,var(--pds-azul),var(--pds-azul-esc)); }
.kpi-grid .kpi-card:nth-child(2)::before{ background:linear-gradient(90deg,var(--pds-ouro),var(--pds-laranja)); }
.kpi-grid .kpi-card:nth-child(3)::before{ background:linear-gradient(90deg,var(--pds-vermelho),var(--pds-maroon)); }
.kpi-card:hover{ border-color:var(--pds-ouro); box-shadow:0 10px 24px rgba(245,121,30,.14); }
.kpi-card.active-filter{ border-color:var(--pds-laranja); }
.kpi-card.active-filter::after{ background:linear-gradient(90deg,var(--pds-ouro),var(--pds-laranja)); }

/* ── Tabela: hover quente ── */
.data-table tbody tr:hover td{ background:#FBF8F4; }

/* ── Filtros (pills) ── */
.filter-pill:hover{ border-color:var(--pds-ouro); color:var(--pds-tinta-warm); background:#FFF6E6; }
.filter-pill.active{ border-color:var(--pds-laranja); color:var(--pds-tinta-warm); background:#FFF1DF; }

/* ── Paginação ── */
.pg-btn:hover{ background:#FFF1DF; }
.pg-btn.active{ background:linear-gradient(135deg,var(--pds-laranja),var(--pds-vermelho)); border-color:transparent; color:#fff; }
```

> **Por que `repeat(3,1fr)`:** o dashboard renderiza **3** KPIs (Total, Ativas, Volume), mas o grid
> original é `repeat(4,1fr)`. Ajustar para 3 faz a linha preencher certinho. Se um dia voltar a ter
> 4 cartões, troque de volta para 4.
>
> **Ícones e valores dos KPIs:** o fundo dos ícones e algumas cores são definidos por `style="..."`
> inline no `EntitySelector.vue` e **continuam azuis/verdes** na Faixa A. A faixa de cor no topo já
> traz o tom quente. Para colorir o cartão inteiro como no mockup, ver o passo 06.

---

## 4.2 Critérios de aceite

- [ ] Os 3 KPIs ganham uma faixa colorida no topo (teal, ouro→laranja, vermelho) e preenchem a linha.
- [ ] Hover dos cartões e das linhas da tabela fica em tom quente.
- [ ] Filtros "Todos/Ativa/Em Análise" e a paginação ativa usam laranja/ouro (não azul).

## 4.3 Reversão

Remova esta subseção do bloco do tema.

> Próximo: `05-botoes-inputs-acentos.md`.
