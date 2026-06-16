# Passo 01 — Fundação: funções de validação compartilhadas

> **Objetivo:** criar funções **puras** (sem efeito colateral) de validação de CNPJ/CPF com
> **dígito verificador** e de parsing matriz/filial, em **frontend** e **backend**.
> Este passo **não altera nenhum fluxo** — só adiciona dois arquivos novos. Impossível quebrar o
> site. Todos os passos seguintes importam daqui.

**Depende de:** nada.
**Arquivos novos:** `utils/validadores.ts`, `validadores.py`.
**Arquivos alterados:** nenhum.

---

## 1.1 Frontend — `utils/validadores.ts`

Crie o arquivo `utils/validadores.ts` (na raiz do projeto Nuxt; auto-importável como módulo).

```ts
// utils/validadores.ts
// Funções puras de validação. Sem dependências externas.

/** Remove tudo que não é dígito. */
export function apenasDigitos(valor: string | null | undefined): string {
  return (valor || '').replace(/\D/g, '')
}

/** Valida CPF (11 dígitos) com dígito verificador. */
export function validarCPF(cpfRaw: string): boolean {
  const cpf = apenasDigitos(cpfRaw)
  if (cpf.length !== 11) return false
  if (/^(\d)\1{10}$/.test(cpf)) return false // todos iguais (000... 111...)

  const calcDV = (base: string, pesoInicial: number): number => {
    let soma = 0
    for (let i = 0; i < base.length; i++) {
      soma += parseInt(base[i], 10) * (pesoInicial - i)
    }
    const resto = (soma * 10) % 11
    return resto === 10 ? 0 : resto
  }

  const dv1 = calcDV(cpf.slice(0, 9), 10)
  if (dv1 !== parseInt(cpf[9], 10)) return false
  const dv2 = calcDV(cpf.slice(0, 10), 11)
  if (dv2 !== parseInt(cpf[10], 10)) return false
  return true
}

/** Valida CNPJ (14 dígitos) com dígito verificador. */
export function validarCNPJ(cnpjRaw: string): boolean {
  const cnpj = apenasDigitos(cnpjRaw)
  if (cnpj.length !== 14) return false
  if (/^(\d)\1{13}$/.test(cnpj)) return false

  const calcDV = (base: string): number => {
    // pesos da Receita: começa em 5 e cai até 2, depois reinicia em 9..2
    let soma = 0
    let peso = base.length - 7
    for (let i = 0; i < base.length; i++) {
      soma += parseInt(base[i], 10) * peso
      peso = peso - 1 < 2 ? 9 : peso - 1
    }
    const resto = soma % 11
    return resto < 2 ? 0 : 11 - resto
  }

  const dv1 = calcDV(cnpj.slice(0, 12))
  if (dv1 !== parseInt(cnpj[12], 10)) return false
  const dv2 = calcDV(cnpj.slice(0, 13))
  if (dv2 !== parseInt(cnpj[13], 10)) return false
  return true
}

export type TipoEstabelecimento = 'MATRIZ' | 'FILIAL' | 'INDEFINIDO'

export interface CnpjPartes {
  raiz: string          // 8 primeiros dígitos
  ordem: string         // 4 dígitos após a barra (ex.: "0001")
  dv: string            // 2 dígitos verificadores
  tipo: TipoEstabelecimento
  numeroFilial: number | null // 1 para matriz, 2,3,... para filiais
}

/** Decompõe o CNPJ em raiz/ordem/dv e classifica matriz x filial. */
export function parseCnpj(cnpjRaw: string): CnpjPartes {
  const cnpj = apenasDigitos(cnpjRaw)
  if (cnpj.length !== 14) {
    return { raiz: '', ordem: '', dv: '', tipo: 'INDEFINIDO', numeroFilial: null }
  }
  const raiz = cnpj.slice(0, 8)
  const ordem = cnpj.slice(8, 12)
  const dv = cnpj.slice(12, 14)
  const numeroFilial = parseInt(ordem, 10)
  const tipo: TipoEstabelecimento = ordem === '0001' ? 'MATRIZ' : 'FILIAL'
  return { raiz, ordem, dv, tipo, numeroFilial }
}

/** Formata 14 dígitos como 00.000.000/0000-00. Tolerante a entrada parcial. */
export function formatarCnpj(cnpjRaw: string): string {
  const c = apenasDigitos(cnpjRaw).slice(0, 14)
  return c
    .replace(/^(\d{2})(\d)/, '$1.$2')
    .replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3')
    .replace(/\.(\d{3})(\d)/, '.$1/$2')
    .replace(/(\d{4})(\d)/, '$1-$2')
}
```

> As máscaras de input que já existem em `EntityCreateForm.vue` (`handleCnpjInput`,
> `handleCpfInput`) **podem ser mantidas**; os passos seguintes só adicionam as funções de
> **validação** (DV) e **parsing** acima.

---

## 1.2 Backend — `validadores.py`

Crie `validadores.py` na raiz (mesmo nível de `main.py`).

```python
# validadores.py
# Funções puras espelhando utils/validadores.ts. O backend é a autoridade.
import re


def apenas_digitos(valor) -> str:
    return re.sub(r"\D", "", valor or "")


def validar_cpf(cpf_raw: str) -> bool:
    cpf = apenas_digitos(cpf_raw)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    def calc_dv(base: str, peso_inicial: int) -> int:
        soma = sum(int(d) * (peso_inicial - i) for i, d in enumerate(base))
        resto = (soma * 10) % 11
        return 0 if resto == 10 else resto

    if calc_dv(cpf[:9], 10) != int(cpf[9]):
        return False
    if calc_dv(cpf[:10], 11) != int(cpf[10]):
        return False
    return True


def validar_cnpj(cnpj_raw: str) -> bool:
    cnpj = apenas_digitos(cnpj_raw)
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    def calc_dv(base: str) -> int:
        soma = 0
        peso = len(base) - 7
        for d in base:
            soma += int(d) * peso
            peso = 9 if peso - 1 < 2 else peso - 1
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    if calc_dv(cnpj[:12]) != int(cnpj[12]):
        return False
    if calc_dv(cnpj[:13]) != int(cnpj[13]):
        return False
    return True


def parse_cnpj(cnpj_raw: str) -> dict:
    cnpj = apenas_digitos(cnpj_raw)
    if len(cnpj) != 14:
        return {"raiz": "", "ordem": "", "dv": "", "tipo": "INDEFINIDO", "numero_filial": None}
    ordem = cnpj[8:12]
    return {
        "raiz": cnpj[:8],
        "ordem": ordem,
        "dv": cnpj[12:14],
        "tipo": "MATRIZ" if ordem == "0001" else "FILIAL",
        "numero_filial": int(ordem),
    }
```

---

## 1.3 Critérios de aceite

- [ ] Os dois arquivos existem e **importam sem erro** (`python -c "import validadores"`).
- [ ] `validarCNPJ('11.222.333/0001-81')` → o número de exemplo válido retorna `true`; um número
      com último dígito trocado retorna `false`.
- [ ] `validarCPF` rejeita `111.111.111-11` e aceita um CPF real válido.
- [ ] `parseCnpj('11222333000181').tipo === 'MATRIZ'`; `...000281` → `'FILIAL'`, `numeroFilial: 2`.
- [ ] O app continua subindo normalmente (nada foi ligado ainda).

## 1.4 Segurança / reversão

100% aditivo. Para reverter, basta apagar os dois arquivos — nenhum outro código os referencia
ainda.

> Próximo: `02-migracao-schema.md`.
