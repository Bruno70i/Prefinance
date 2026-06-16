# Passo 01 — Backend: `GET /api/entidades/{id}` com dados aninhados

> **Objetivo:** criar um endpoint que devolva **todos** os dados de uma entidade no formato que o
> wizard consome — colunas de formalização + `configuracoes_extras` + objeto `parceria` + lista
> `repasses`. Sem ele, o modo de edição (passo 02) não tem como preencher o formulário.
>
> 100% **aditivo**: nenhuma rota existente muda. Impossível quebrar a UI.

**Depende de:** nada.
**Arquivos alterados:** `main.py`.

---

## 1.1 ⚠️ Cuidado com a ordem das rotas (evita conflito)

Já existem rotas estáticas sob `/api/entidades/...`:
`GET /api/entidades/check-cnpj`, `GET /api/entidades/por-raiz/{raiz}`, `GET /api/entidades/check-razao`.

No FastAPI as rotas são avaliadas **na ordem de registro**. Se você declarar
`GET /api/entidades/{entidade_id}` **antes** dessas estáticas, a chamada a `/api/entidades/check-cnpj`
seria capturada como `entidade_id="check-cnpj"`.

➡️ **Declare o novo endpoint DEPOIS de todas as rotas estáticas `/api/entidades/...`** — por
exemplo, logo acima de `update_entidade` (`@app.put("/api/entidades/{entidade_id}")`, ~linha 824).

## 1.2 Implementação

Reaproveite a lógica de leitura que o export por entidade já usa (join com `dados_parceria` e
busca em `repasses_mensais`). Acrescente em `main.py`:

```python
@app.get("/api/entidades/{entidade_id}")
def get_entidade_completa(entidade_id: str):
    """Retorna uma entidade com formalização + parceria + repasses aninhados (para edição)."""
    if not engine:
        raise HTTPException(status_code=500, detail="Banco de dados não inicializado.")
    try:
        uuid.UUID(entidade_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de entidade inválido (UUID).")

    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT e.*,
                   p.ajuste_termo, p.inicio_atividades, p.termino_atividades, p.gestor_parceria,
                   p.projeto, p.categorias, p.atendimento_descricao, p.meta_mes_atendimentos,
                   p.responsavel_entidade, p.especialidades
            FROM entidades e
            LEFT JOIN dados_parceria p ON e.id = p.entidade_id
            WHERE e.id = :id
        """), {"id": entidade_id}).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Entidade não encontrada.")
        m = row._mapping

        reps = conn.execute(text("""
            SELECT * FROM repasses_mensais
            WHERE entidade_id = :id
            ORDER BY mes_referencia ASC
        """), {"id": entidade_id}).fetchall()

    def d(v):  # date -> 'YYYY-MM-DD'
        return v.isoformat() if v is not None and hasattr(v, "isoformat") else (v or None)

    extras = m["configuracoes_extras"] or {}

    return {
        "id": str(m["id"]),
        # --- Formalização (colunas reais) ---
        "razao_social": m["razao_social"],
        "cnpj": m["cnpj"],
        "responsavel_nome": m["responsavel_nome"],
        "situacao": m["situacao"],
        "historico": m["historico"],
        "pa_emenda": m["pa_emenda"],
        "localizacao_pa_emenda": m["localizacao_pa_emenda"],
        "emenda_alterada": m["emenda_alterada"],
        "pa_formalizacao": m["pa_formalizacao"],
        "numero_emenda": m["numero_emenda"],
        "vereador": m["vereador"],
        "justificativa": m["justificativa"],
        "valor": float(m["valor"]) if m["valor"] is not None else None,
        "cod_scim": m["cod_scim"],
        "pa_empenho": m["pa_empenho"],
        "objeto_descricao": m["objeto_descricao"],
        "configuracoes_extras": extras,
        # --- Parceria (tabela 1:1) ---
        "parceria": {
            "ajuste_termo": m["ajuste_termo"],
            "inicio_atividades": d(m["inicio_atividades"]),
            "termino_atividades": d(m["termino_atividades"]),
            "gestor_parceria": m["gestor_parceria"],
            "projeto": m["projeto"],
            "categorias": m["categorias"] or {},
            "atendimento_descricao": m["atendimento_descricao"],
            "meta_mes_atendimentos": m["meta_mes_atendimentos"] or 0,
            "responsavel_entidade": m["responsavel_entidade"],
            "especialidades": m["especialidades"] or {},
        },
        # --- Repasses (tabela 1:N) ---
        "repasses": [
            {
                "mes_referencia": r._mapping["mes_referencia"],
                "repasse_oficio": r._mapping["repasse_oficio"],
                "repasse_periodo": r._mapping["repasse_periodo"],
                "repasse_parcela": float(r._mapping["repasse_parcela"] or 0),
                "repasse_retencao": float(r._mapping["repasse_retencao"] or 0),
                "repasse_valor_final": float(r._mapping["repasse_valor_final"] or 0),
                "repasse_vencimento": d(r._mapping["repasse_vencimento"]),
                "repasse_pa": r._mapping["repasse_pa"],
                "repasse_data_pagamento": d(r._mapping["repasse_data_pagamento"]),
                "prestacao_oficio": r._mapping["prestacao_oficio"],
                "prestacao_data_entrega": d(r._mapping["prestacao_data_entrega"]),
                "prestacao_pa": r._mapping["prestacao_pa"],
                "prestacao_sugestao_glosa": float(r._mapping["prestacao_sugestao_glosa"] or 0),
                "prestacao_reconsideracao": float(r._mapping["prestacao_reconsideracao"] or 0),
                "prestacao_mts": r._mapping["prestacao_mts"],
            } for r in reps
        ],
    }
```

> **Nota sobre `categorias`:** o schema Pydantic trata como `Dict[str, bool]`. O wizard usa
> `form.parceria.categorias[cat]` (checkbox). Devolva o JSONB como veio; o passo 02 mapeia.

## 1.3 (Opcional) Limpeza de rota duplicada

Há **duas** definições de `@app.get("/api/entidades")` (≈ linhas 261 e 704). A segunda é
inalcançável (a primeira sempre vence). Pode remover a segunda num passo de limpeza (ver arquivo
04). **Não** é obrigatório para este passo.

---

## 1.4 Critérios de aceite

- [ ] `GET /api/entidades/{id_existente}` retorna `200` com `parceria` (objeto) e `repasses` (lista).
- [ ] Datas vêm como `YYYY-MM-DD`; `valor` e parcelas como número.
- [ ] `GET /api/entidades/check-cnpj?cnpj=...` **continua funcionando** (não foi capturado pela rota
      `{id}`) — confirme que a ordem de registro está correta.
- [ ] `GET /api/entidades/{uuid_inexistente}` → `404`.
- [ ] A UI atual continua idêntica (nada foi religado ainda).

## 1.5 Segurança / reversão

Só leitura, aditivo. Reverter = remover o endpoint.

> Próximo: `02-edicao-reusa-wizard.md`.
