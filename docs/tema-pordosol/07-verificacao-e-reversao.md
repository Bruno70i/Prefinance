# Passo 07 — Verificação por tela e reversão total

> **Objetivo:** validar o tema em todas as telas sem regressões e documentar como reverter 100%.

---

## 7.1 Checklist de verificação (rode `npm run dev` e confira)

**Dashboard**
- [ ] Sidebar navy com brilho quente; item ativo dourado.
- [ ] Topbar em degradê quente; título branco; "Nova Parceria" creme.
- [ ] KPIs com cor (faixa — passo 04 — ou inteiros — passo 06); 3 cartões preenchem a linha.
- [ ] Filtros, paginação e hover da tabela em tons quentes.
- [ ] Coluna "Criado por" e botões Editar/Exportar/Excluir continuam funcionando.

**Cadastro de Formalização / Nova Parceria (wizard)**
- [ ] Barra de passos (1·2·3) com o passo ativo em laranja.
- [ ] Foco dos campos em laranja; drop-zone de importação com hover quente.
- [ ] Botão "Efetivar e Concluir" continua **verde** (semântico).
- [ ] Soma das parcelas: `val-ok` verde / `val-err` vermelho mantidos.

**Edição / Painel Admin / Login**
- [ ] Edição usa as mesmas classes → herda o tema automaticamente.
- [ ] `pages/admin.vue` e `pages/login.vue` usam **estilos inline próprios** (definidos nos planos
      anteriores) → não mudam sozinhos. Se quiser alinhar, troque os azuis inline por laranja/ouro
      manualmente (opcional — ver 7.2).

**Assistente IA (chat)**
- [ ] `components/AssistenteIA.vue` tem cores **inline próprias** (botão/cabeçalho navy/azul). Funciona
      normalmente; para combinar, ver 7.2 (opcional).

**Funcional (não-regressão)**
- [ ] Exportação Excel, importação, chat, login/logout e CRUD continuam idênticos.
- [ ] Nenhum erro no console; nada de layout quebrado em telas menores (o `@media` original segue valendo).

## 7.2 (Opcional) Aquecer os componentes de estilo inline

Esses filhos não usam as classes globais, então ficam de fora do tema. Ajuste pontual se desejar:
- **`components/AssistenteIA.vue`**: nos estilos `.ia-fab` e `.ia-header`, troque
  `#0b5394` por `#F5791E` (ou um gradiente `linear-gradient(135deg,#F5791E,#E0241F)`).
- **`pages/login.vue`**: troque o azul do botão/título por laranja/ouro.
- **`pages/admin.vue`**: usa classes `.btn-*` → já herda o tema; ajuste só se houver azul inline.

> São melhorias cosméticas opcionais; não são necessárias para o tema funcionar.

## 7.3 Reversão total (voltar ao azul original)

1. No `assets/css/main.css`, apague tudo entre
   `/* ===== TEMA PÔR DO SOL — INÍCIO ===== */` e `/* ===== TEMA PÔR DO SOL — FIM ===== */`.
2. No `nuxt.config.ts`, remova `Plus+Jakarta+Sans:...` do link de fonte.
3. Se fez o passo 06: remova as 3 classes `kpi-sun*` no `EntitySelector.vue`.

Pronto — o app volta exatamente ao estado anterior, sem resíduos. **Nada no backend foi tocado em
nenhum momento.**

---

## 7.4 Resumo dos artefatos

| Arquivo | Mudança |
|---|---|
| `assets/css/main.css` | + bloco `TEMA PÔR DO SOL` no final (passos 01–06) |
| `nuxt.config.ts` | + fonte Plus Jakarta Sans no link (opcional) |
| `components/EntitySelector.vue` | + 3 classes nos KPIs (só passo 06, opcional) |

> **Nenhuma rota, endpoint, modelo ou lógica de Vue alterada.** O tema é puramente visual e
> reversível. Fim do plano — volte ao `00-INDICE-E-ORDEM.md`.
