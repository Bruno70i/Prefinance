# Passo 01 — Base: bloco do tema, tokens, fundo e fonte

> **Objetivo:** abrir o bloco de tema no fim do `main.css`, declarar os tokens de cor, aplicar o
> fundo quente e (opcional) trocar a fonte para Plus Jakarta Sans.

**Arquivos alterados:** `assets/css/main.css` (acréscimo no fim), `nuxt.config.ts` (1 link de fonte).

---

## 1.1 (Opcional, recomendado) Fonte Plus Jakarta Sans

Em `nuxt.config.ts`, dentro de `app.head.link`, a fonte atual carrega DM Sans + DM Mono. **Acrescente**
a família Plus Jakarta Sans no mesmo link do Google Fonts (ou adicione um novo link):

```ts
{ rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap' }
```
> Mudança mínima: só estende o parâmetro `family=`. Se preferir não trocar a fonte, pule este item —
> o tema funciona igual com DM Sans.

## 1.2 Abrir o bloco de tema no FIM do `main.css`

Acrescente ao **final** de `assets/css/main.css` (depois da última linha existente):

```css
/* ====================== TEMA PÔR DO SOL — INÍCIO ====================== */
:root{
  --pds-bg:#F3F0EC;
  --pds-tinta:#15212E; --pds-cinza:#5C6B7A;
  --pds-azul:#13A0B0; --pds-azul-esc:#0A6E7E;          /* teal (toque frio) */
  --pds-vermelho:#E0241F; --pds-maroon:#8C1410;
  --pds-ouro:#FBBE12; --pds-laranja:#F5791E; --pds-laranja2:#FF9A3D;
  --pds-navy1:#14304F; --pds-navy2:#0A1B30;
  --pds-cream:#FFE7CF; --pds-tinta-warm:#A23410;
  --pds-side-txt:#CDBFA9; --pds-side-sub:#9A8C78;
}

/* Fundo quente + leve brilho (como o mockup) */
body{ background:var(--pds-bg); }
body::before{
  content:""; position:fixed; inset:0; z-index:-1; pointer-events:none;
  background:
    radial-gradient(900px 420px at 82% -6%, rgba(245,121,30,.12), transparent),
    radial-gradient(700px 380px at 8% 106%, rgba(224,36,31,.08), transparent);
}

/* Fonte (só se você fez o item 1.1) */
body,
.btn, .filter-pill, .pg-btn,
input[type=text], input[type=date], input[type=email], input[type=number],
select, textarea, #main-search{
  font-family:'Plus Jakarta Sans','DM Sans',sans-serif;
}
/* ======================  TEMA PÔR DO SOL — FIM  ====================== */
```

> Os próximos passos (02–05) **inserem suas regras ANTES da linha `FIM`**, dentro deste mesmo bloco.

---

## 1.3 Critérios de aceite

- [ ] O fundo do app fica bege/quente (`#F3F0EC`) em vez do cinza-azulado.
- [ ] (Se fez 1.1) os textos usam Plus Jakarta Sans; campos mono seguem em DM Mono.
- [ ] Nada quebrou: dashboard, cadastro, edição, exportação, chat e login funcionam igual.

## 1.4 Reversão

Apague o bloco `TEMA PÔR DO SOL` do `main.css` e remova `Plus+Jakarta+Sans` do link em
`nuxt.config.ts`.

> Próximo: `02-sidebar.md`.
