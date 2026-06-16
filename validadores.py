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
