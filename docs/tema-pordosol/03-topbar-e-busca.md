# Passo 03 — Topbar em degradê quente + busca

> **Objetivo:** transformar a barra do topo (branca) no degradê quente do mockup
> (laranja→vermelho→ouro) com o botão "Nova Parceria" em creme, e dar foco laranja à busca.

**Arquivos alterados:** `assets/css/main.css` (bloco do tema).

---

## 3.1 CSS (acrescentar ao bloco do tema)

```css
/* ── Topbar (Pôr do Sol) ── */
.top-bar{
  background:linear-gradient(100deg,var(--pds-laranja) 0%,var(--pds-vermelho) 58%,var(--pds-ouro) 128%);
  border-bottom:none; position:sticky; overflow:hidden;
}
.top-bar::after{ /* brilho de "sol" no canto direito */
  content:""; position:absolute; right:-30px; top:-60px; width:220px; height:220px; border-radius:50%;
  background:radial-gradient(circle, rgba(255,233,160,.5), transparent 62%); pointer-events:none;
}
.top-bar-left h2{ color:#fff; position:relative; z-index:1; }
.breadcrumb{ color:#FFE7CF; position:relative; z-index:1; }

/* "Nova Parceria" (btn-primary dentro da topbar) vira creme para contrastar */
.top-bar .btn-primary{
  background:linear-gradient(135deg,#fff,var(--pds-cream)); color:var(--pds-tinta-warm);
  position:relative; z-index:1;
}
.top-bar .btn-primary:hover{ box-shadow:0 4px 12px rgba(0,0,0,.18); transform:translateY(-1px); }

/* ── Busca: foco quente ── */
#main-search:focus{ border-color:var(--pds-laranja); box-shadow:0 0 0 4px rgba(245,121,30,.12); }
```

> O seletor `.top-bar .btn-primary` é mais específico que `.btn-primary`, então vence o estilo
> laranja global (passo 05) **apenas dentro da topbar**, deixando o botão em creme exatamente como
> no mockup.

---

## 3.2 Critérios de aceite

- [ ] A barra do topo fica em degradê quente com um brilho de sol à direita.
- [ ] O título "Dashboard de Consulta" e o breadcrumb ficam brancos/claros e legíveis.
- [ ] O botão "＋ Nova Parceria" fica creme com texto laranja-escuro.
- [ ] Ao focar a busca, o anel fica laranja (não azul).

## 3.3 Reversão

Remova esta subseção do bloco do tema.

> Próximo: `04-kpis-tabela-pills.md`.
