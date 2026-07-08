# Passo 05 — Botões, inputs e acentos diversos

> **Objetivo:** trocar o azul restante (botão primário, foco de inputs, badge de contexto, passos do
> wizard, drop-zone) pelos tons quentes, mantendo as cores semânticas (verde/vermelho).

**Arquivos alterados:** `assets/css/main.css` (bloco do tema).

---

## 5.1 CSS (acrescentar ao bloco do tema)

```css
/* ── Botão primário (em fundo claro) → gradiente quente ── */
.btn-primary{ background:linear-gradient(135deg,var(--pds-ouro),var(--pds-laranja)); color:#3A2400; }
.btn-primary:hover{ background:linear-gradient(135deg,var(--pds-laranja),var(--pds-vermelho)); color:#fff; box-shadow:0 6px 16px rgba(245,121,30,.32); transform:translateY(-1px); }
/* (a topbar já tem .top-bar .btn-primary creme, mais específico — vence lá dentro) */

/* ── Botão ghost (fora da sidebar): hover quente ── */
.btn-ghost:hover{ background:#FFF6E6; border-color:var(--pds-ouro); color:var(--pds-tinta-warm); }

/* ── Inputs: foco quente ── */
input[type=text]:focus, input[type=date]:focus, input[type=email]:focus,
input[type=number]:focus, select:focus, textarea:focus{
  border-color:var(--pds-laranja); box-shadow:0 0 0 3px rgba(245,121,30,.12);
}

/* ── Context badge (telas 2 e 3) ── */
.context-badge{ background:linear-gradient(135deg,#FFF6E6,#FFE9CF); border-color:#FBD89A; }
.context-badge .cb-label{ color:#C98A2A; }
.context-badge .cb-value{ color:var(--pds-tinta-warm); }
.context-badge .cb-sep{ background:#FBD89A; }

/* ── Step progress (wizard) ── */
.step.active{ color:var(--pds-tinta-warm); }
.step.active .step-circle{ border-color:var(--pds-laranja); background:linear-gradient(135deg,var(--pds-laranja),var(--pds-vermelho)); color:#fff; }

/* ── Drop-zone (upload / importação) ── */
.drop-zone:hover, .drop-zone.dragover{ border-color:var(--pds-laranja); background:#FFF6E6; }
```

> **Mantido de propósito (cores semânticas):**
> - `.btn-success` (verde, "Efetivar e Concluir") e `.btn-danger` (vermelho, excluir) — continuam.
> - `.badge-ativa` (verde) / `.badge-em_analise` (amarelo) — continuam, pois comunicam status. Veja a
>   opção de aquecer abaixo, se quiser.
> - `.val-ok` (verde) / `.val-err` (vermelho) da soma de parcelas — continuam.

### (Opcional) Aquecer os badges de status
Se preferir os badges com a cara do mockup (em vez de verde/amarelo), adicione:
```css
.badge-ativa{ background:linear-gradient(135deg,rgba(245,121,30,.16),rgba(245,121,30,.06)); color:var(--pds-tinta-warm); }
.badge-ativa .badge-dot{ background:var(--pds-laranja); }
.badge-em_analise{ background:linear-gradient(135deg,rgba(251,190,18,.22),rgba(245,121,30,.10)); color:#8A5A00; }
.badge-em_analise .badge-dot{ background:var(--pds-ouro); }
```

---

## 5.2 Critérios de aceite

- [ ] Botões primários (fora da topbar) ficam em gradiente ouro→laranja.
- [ ] Foco de qualquer input/seletor/textarea fica laranja.
- [ ] Wizard (passos), context-badge e drop-zone usam tons quentes.
- [ ] "Efetivar" segue verde e "Excluir" segue vermelho (semântica preservada).

## 5.3 Reversão

Remova esta subseção do bloco do tema.

> Próximo: `06-opcional-kpis-coloridos.md` (opcional) ou `07-verificacao-e-reversao.md`.
