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
