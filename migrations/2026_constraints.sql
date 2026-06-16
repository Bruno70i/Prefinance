-- migrations/2026_constraints.sql
-- Constraints de integridade no banco de dados para evitar inconsistência de valores.

-- 1) Valor total não-negativo na entidade
ALTER TABLE entidades ADD CONSTRAINT chk_valor_nao_negativo CHECK (valor IS NULL OR valor >= 0);

-- 2) Vigência correta (início <= término) na parceria
ALTER TABLE dados_parceria ADD CONSTRAINT chk_vigencia CHECK (
    inicio_atividades IS NULL OR termino_atividades IS NULL OR termino_atividades >= inicio_atividades
);

-- 3) Parcela de repasses mensais não-negativa
ALTER TABLE repasses_mensais ADD CONSTRAINT chk_parcela_nao_negativa CHECK (repasse_parcela IS NULL OR repasse_parcela >= 0);
