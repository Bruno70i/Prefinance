# Passo 02 — Sidebar navy com brilho quente

> **Objetivo:** transformar a sidebar branca atual no painel navy do mockup, com a navegação ativa em
> ouro/laranja e o avatar quente.

**Arquivos alterados:** `assets/css/main.css` (dentro do bloco do tema, antes da linha `FIM`).

---

## 2.1 CSS (acrescentar ao bloco do tema)

```css
/* ── Sidebar (Pôr do Sol) ── */
.sidebar{ background:linear-gradient(180deg,var(--pds-navy1),var(--pds-navy2)); border-right:1px solid rgba(255,255,255,.06); overflow:hidden; }
.sidebar::after{ /* brilho quente no rodapé */
  content:""; position:absolute; left:0; right:0; bottom:-30px; height:130px; pointer-events:none;
  background:
    radial-gradient(130px 70px at 35% 50%, rgba(251,190,18,.22), transparent),
    radial-gradient(130px 70px at 78% 60%, rgba(245,121,30,.18), transparent);
}
.sidebar-logo{ border-bottom-color:rgba(255,255,255,.10); }
.sidebar-logo h1{ color:#fff; }
.sidebar-logo p{ color:var(--pds-side-sub); }
.org-badge{ background:rgba(251,190,18,.14); color:var(--pds-ouro); }
.nav-section-label{ color:var(--pds-side-sub); }

.nav-item{ color:var(--pds-side-txt); }
.nav-item:hover{ background:rgba(255,255,255,.05); color:#fff; }
.nav-item.active{ background:linear-gradient(90deg,rgba(251,190,18,.24),rgba(245,121,30,.14)); color:#fff; }
.nav-item.active::before{ background:linear-gradient(180deg,var(--pds-ouro),var(--pds-laranja)); }

.nav-icon-wrap{ background:rgba(255,255,255,.10); }
.nav-item.active .nav-icon-wrap{ background:linear-gradient(135deg,var(--pds-ouro),var(--pds-laranja)); color:#3A2400; }
.nav-num{ background:rgba(255,255,255,.10); color:#fff; }
.nav-item.active .nav-num{ background:linear-gradient(135deg,var(--pds-ouro),var(--pds-laranja)); color:#3A2400; }
.nav-label-sub{ color:var(--pds-side-sub); }

.sidebar-footer{ border-top-color:rgba(255,255,255,.10); }
.u-name{ color:#fff; }
.u-role{ color:var(--pds-side-sub); }
.user-avatar{ background:linear-gradient(135deg,var(--pds-ouro),var(--pds-laranja)); color:#3A2400; }

/* Botões do rodapé da sidebar (Painel Admin / Sair) legíveis no fundo escuro */
.sidebar .btn-ghost{ color:#EFE6D8; border-color:rgba(255,255,255,.18); background:rgba(255,255,255,.06); }
.sidebar .btn-ghost:hover{ background:rgba(255,255,255,.12); border-color:rgba(255,255,255,.28); color:#fff; }
```

> **Sobre os ícones:** os SVGs da nav usam `stroke="currentColor"`, então acompanham a cor do
> `.nav-item` automaticamente — ficam claros no fundo escuro sem editar markup.
>
> **Botão "Sair":** se ele tiver uma cor vermelha via `style="color:#ef4444"` inline, ela
> permanece (e fica boa sobre o escuro). Não precisa mexer.

---

## 2.2 Critérios de aceite

- [ ] A sidebar fica navy com leve brilho dourado/laranja no rodapé.
- [ ] "PreFinance" branco; o item ativo tem realce dourado e barra lateral em degradê ouro→laranja.
- [ ] Avatar "BR" com gradiente quente; nome do usuário branco, cargo em tom areia.
- [ ] "Painel Admin"/"Sair" continuam legíveis e clicáveis.

## 2.3 Reversão

Remova esta subseção do bloco do tema.

> Próximo: `03-topbar-e-busca.md`.
