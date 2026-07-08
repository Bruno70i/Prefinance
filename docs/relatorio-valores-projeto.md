# Relatório de Horas e Justificativa de Valores
## Projeto PreFinance — Sistema de Gestão de Parcerias (Terceiro Setor / OSC-ONG)

| | |
|---|---|
| **Prestador de serviço** | Bruno Nascimento |
| **Sistema** | PreFinance — Gestão de Parcerias, Repasses e Prestação de Contas |
| **Modelo de cobrança** | Por hora efetivamente trabalhada |
| **Data do relatório** | 23/06/2026 |

---

## 1. Resumo executivo

Este relatório apresenta a memória de cálculo e a justificativa do valor referente ao
desenvolvimento do sistema **PreFinance**, uma aplicação web completa para a gestão de parcerias com
o terceiro setor (cadastro, controle financeiro de repasses, prestação de contas, exportação de
planilhas oficiais, assistente de inteligência artificial e controle de acesso).

A cobrança é feita **por hora trabalhada**, a um valor **abaixo da média de mercado**, conforme
detalhado abaixo.

---

## 2. Memória de cálculo

| Item | Valor |
|---|---|
| Horas trabalhadas por dia | **6 horas** |
| Total de dias trabalhados | **12 dias** |
| **Total de horas** | **72 horas** (6 h × 12 dias) |
| Valor da hora | **R$ 80,00** |
| **VALOR TOTAL** | **R$ 5.760,00** (72 h × R$ 80,00) |

> **Valor total do projeto: R$ 5.760,00** (cinco mil, setecentos e sessenta reais).

---

## 3. Escopo entregue (o que justifica as horas)

O projeto não é um cadastro simples: envolve automação de planilhas, regras de validação, segurança,
inteligência artificial e integração entre frontend, backend e banco de dados. Abaixo, os módulos
entregues e a estimativa de esforço de cada um.

| # | Módulo entregue | Descrição resumida | Horas (estim.) |
|---|---|---|---:|
| 1 | **Exportação Excel institucional** | Geração de planilhas idênticas ao modelo oficial (3 abas, cabeçalhos agrupados, tabela transposta de repasses, formatação avançada). | 12 h |
| 2 | **Validações de dados robustas** | CNPJ/CPF com dígito verificador, vigência (início × término), conciliação da soma de parcelas, detecção de duplicidade, matriz/filial e consulta automática de CNPJ. | 14 h |
| 3 | **Edição unificada + exportação por entidade** | Padronização do formulário de edição com o de cadastro e exportação individual de cada parceria. | 8 h |
| 4 | **Assistente de Inteligência Artificial** | Chat com IA **local** (privacidade total) capaz de responder sobre qualquer cadastro, com dados buscados diretamente do banco. | 10 h |
| 5 | **Importação de planilhas** | Leitura de Excel/CSV com preenchimento automático do formulário (processo inverso da exportação) + modelo para download. | 8 h |
| 6 | **Login, painel administrativo e auditoria** | Autenticação de usuários, painel `/admin` para gestão e recuperação de senha, e registro de autoria (quem criou cada parceria, com data e hora). | 12 h |
| 7 | **Identidade visual / tema** | Definição da paleta institucional e aplicação do novo visual em todo o sistema. | 4 h |
| 8 | **Documentação técnica** | Documentação detalhada de cada módulo, em etapas, para manutenção e evolução futuras. | 4 h |
| | **TOTAL** | | **72 h** |

---

## 4. Justificativa do valor da hora (R$ 80,00)

- **Abaixo do mercado:** o valor-hora de um desenvolvedor *full-stack* com este conjunto de
  tecnologias costuma variar entre **R$ 100,00 e R$ 200,00+** por hora. O valor praticado aqui
  (**R$ 80,00**) está **deliberadamente abaixo** dessa faixa.
- **Trabalho especializado:** o projeto reúne várias competências em uma só entrega:
  - Frontend moderno (Nuxt 3 / Vue 3, TypeScript);
  - Backend em Python (FastAPI) com banco de dados PostgreSQL;
  - Automação de planilhas Excel (geração e leitura);
  - Inteligência artificial local (Ollama / LLM);
  - Segurança (autenticação, hashing de senhas, controle de acesso);
  - Regras de negócio e validações específicas do terceiro setor.
- **Valor entregue:** um sistema que **substitui controles manuais em planilhas soltas**, reduz erro
  de digitação, padroniza documentos oficiais e centraliza a informação — com ganho direto de tempo
  e confiabilidade para a equipe.

---

## 5. Resumo financeiro

| Descrição | Quantidade | Valor unitário | Subtotal |
|---|---:|---:|---:|
| Desenvolvimento do sistema PreFinance (por hora) | 72 h | R$ 80,00 | R$ 5.760,00 |
| | | **TOTAL GERAL** | **R$ 5.760,00** |

---

## 6. Observações

- Valores expressos em reais (BRL).
- O total contempla o desenvolvimento descrito na seção 3.
- Itens não inclusos (caso aplicável, a combinar à parte): hospedagem/infraestrutura, manutenção
  mensal, suporte contínuo e novas funcionalidades futuras.

---

*Relatório gerado em 23/06/2026 — Projeto PreFinance.*
