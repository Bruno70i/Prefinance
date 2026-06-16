# Passo 10 — Dicas extras e melhorias de robustez

> Melhorias complementares, independentes entre si. Implemente conforme prioridade. Cada uma é
> aditiva e não quebra os passos anteriores.

---

## 10.1 ⚠️ Padronizar `mes_referencia` (bug latente importante)

**Problema:** o formulário deixa digitar o mês livremente — `EntityCreateForm.vue` ~linha 339:
`placeholder="Ex Janeiro/2025"`. Mas a **exportação Excel** (ver `modelo/LAYOUT_EXPORT_EXCEL.md` e
`excel_modelo.py`, função `build_sheet_repasse`) **pivota as colunas por `MM.AAAA`** (ex.: `01.2025`).
Se o usuário digitar "Janeiro/2025", a parcela **não casa** com nenhuma coluna e **some** da
planilha.

**Correção recomendada:**
- Trocar o input de texto por **dois selects** (mês 01–12 + ano) ou um `<input type="month">`, e
  gravar sempre no formato `MM.AAAA`.
- Migração de dados: normalizar registros antigos em `repasses_mensais.mes_referencia` para `MM.AAAA`
  (script único, mapeando nomes de mês → número).
- Validação backend no `RepasseCreate`: regex `^\d{2}\.\d{4}$`.

```python
# em RepasseCreate (main.py), validação de formato:
from pydantic import field_validator
import re

@field_validator("mes_referencia")
@classmethod
def _formato_mes(cls, v: str) -> str:
    if v and not re.fullmatch(r"\d{2}\.\d{4}", v.strip()):
        raise ValueError("mes_referencia deve estar no formato MM.AAAA (ex.: 01.2026).")
    return v.strip()
```

> **Alto valor:** isso conecta diretamente com o trabalho de exportação já entregue. Sem isso, o
> Excel pode sair com meses em branco.

## 10.2 Normalização consistente de CNPJ/CPF/telefone

- Armazenar **sempre apenas dígitos** (o passo 02 já faz isso para CPF/telefone; garanta o mesmo
  para CNPJ no create/update).
- Exibir formatado na UI via `formatarCnpj` (passo 01) — separar **armazenamento** de
  **apresentação**.

## 10.3 Constraints de banco (última linha de defesa)

Adicionar via migração (mesmo padrão do passo 02):
```sql
ALTER TABLE entidades         ADD CONSTRAINT chk_valor_nao_negativo CHECK (valor IS NULL OR valor >= 0);
ALTER TABLE dados_parceria    ADD CONSTRAINT chk_vigencia CHECK (
    inicio_atividades IS NULL OR termino_atividades IS NULL OR termino_atividades >= inicio_atividades
);
ALTER TABLE repasses_mensais  ADD CONSTRAINT chk_parcela_nao_negativa CHECK (repasse_parcela IS NULL OR repasse_parcela >= 0);
```
> Garante integridade mesmo contra inserts feitos fora da aplicação. Cheque dados existentes antes
> (um CHECK falha se houver linha violando).

## 10.4 Detecção de quase-duplicatas (nome)

Antes de concluir, avisar (🟡) se houver `razao_social` muito parecida com uma já cadastrada
(evita "APAE" vs "A.P.A.E."). Implementável com a extensão `pg_trgm`:
```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
-- endpoint: SELECT razao_social, similarity(razao_social, :nome) AS s
--           FROM entidades WHERE similarity(razao_social, :nome) > 0.5 ORDER BY s DESC LIMIT 5;
```
Mostrar como sugestão, nunca bloqueio.

## 10.5 Modal de confirmação antes de "Efetivar"

Resumo final com: razão social, CNPJ (tipo matriz/filial), total, nº de parcelas, soma conferida,
e os avisos 🟡 ativos (CPF reutilizado, quase-duplicata). Botão "Confirmar e salvar". Reduz erros
de submissão acidental.

## 10.6 Validação de e-mail e telefone

- E-mail: usar `type="email"` (já é) + validação Pydantic com `EmailStr` (requer
  `pydantic[email]`), ou regex simples no backend.
- Telefone: exigir 10 ou 11 dígitos quando preenchido (a máscara já limita; validar no submit).

## 10.7 Mensagens de erro do backend mais específicas

Hoje o catch genérico em `create_entidade` (~linha 361) responde "uma entidade com estes dados já
existe" para qualquer violação de unicidade. Com os passos 02/03, prefira **pré-checagens
explícitas** que dizem exatamente qual campo e qual registro conflita (o passo 03 já faz isso para
CNPJ). Aplique o mesmo padrão a futuras constraints únicas.

## 10.8 Foco automático no primeiro campo inválido

Em `nextStep`/`submitForm`, ao detectar erro, chamar `.focus()` (ou `scrollIntoView`) no primeiro
campo com erro. Melhora muito a UX em formulários longos.

## 10.9 Testes recomendados (rede de segurança)

- Backend: testes de unidade para `validadores.py` (CNPJ/CPF válidos e inválidos conhecidos) e
  testes de API para os 409/400 de duplicidade, datas e soma.
- Front: testes dos computeds `somaCoincide`, `podeConcluir`, `datasVigenciaInvalidas`,
  `cnpjPartes`.

---

## 10.10 Resumo de prioridade sugerida (dentro deste arquivo)

1. **10.1 (mes_referencia)** — corrige bug que afeta a exportação. Alta prioridade.
2. **10.3 (constraints)** — barato e protege contra dados ruins.
3. **10.7 / 10.8** — qualidade de UX e mensagens.
4. **10.4 / 10.5 / 10.6 / 10.9** — refinamentos conforme tempo.

> Fim do plano. Volte ao `00-INDICE-E-ORDEM.md` para a ordem geral de execução.
