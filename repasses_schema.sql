-- 1. Adiciona campos de cabeçalho fixos à tabela principal entidades
ALTER TABLE entidades
    ADD COLUMN IF NOT EXISTS cod_scim VARCHAR(255) NULL,
    ADD COLUMN IF NOT EXISTS pa_empenho VARCHAR(255) NULL,
    ADD COLUMN IF NOT EXISTS objeto_descricao TEXT NULL;

COMMENT ON COLUMN entidades.cod_scim IS 'Código identificador no Sistema SCIM';
COMMENT ON COLUMN entidades.pa_empenho IS 'Número do Processo Administrativo de Empenho';
COMMENT ON COLUMN entidades.objeto_descricao IS 'Descrição detalhada do objeto da parceria/emenda';

-- 2. Cria a nova tabela de repasses mensais (Relação 1:N)
CREATE TABLE IF NOT EXISTS repasses_mensais (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entidade_id UUID NOT NULL REFERENCES entidades(id) ON DELETE CASCADE,
    mes_referencia VARCHAR(20) NOT NULL, -- Formato: MM.AAAA (Ex: 01.2026)
    repasse_oficio VARCHAR(255) NULL,
    repasse_periodo VARCHAR(255) NULL,
    repasse_parcela NUMERIC(15, 2) DEFAULT 0,
    repasse_retencao NUMERIC(15, 2) DEFAULT 0,
    repasse_valor_final NUMERIC(15, 2) DEFAULT 0,
    repasse_vencimento DATE NULL,
    repasse_pa VARCHAR(255) NULL,
    repasse_data_pagamento DATE NULL,
    prestacao_oficio VARCHAR(255) NULL,
    prestacao_data_entrega DATE NULL,
    prestacao_pa VARCHAR(255) NULL,
    prestacao_sugestao_glosa NUMERIC(15, 2) DEFAULT 0,
    prestacao_reconsideracao NUMERIC(15, 2) DEFAULT 0,
    prestacao_mts VARCHAR(255) NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexação para buscas rápidas de repasses vinculados a uma entidade
CREATE INDEX IF NOT EXISTS idx_repasses_entidade ON repasses_mensais(entidade_id);

-- Restrição única para evitar lançamentos duplicados para o mesmo mês na mesma entidade
ALTER TABLE repasses_mensais DROP CONSTRAINT IF EXISTS uq_entidade_mes;
ALTER TABLE repasses_mensais ADD CONSTRAINT uq_entidade_mes UNIQUE (entidade_id, mes_referencia);

-- Comentários das colunas de repasse
COMMENT ON TABLE repasses_mensais IS 'Tabela contendo os lançamentos financeiros e prestações de contas mensais (Relação 1:N)';
