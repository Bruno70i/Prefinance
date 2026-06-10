-- Adiciona novas colunas de formalização à tabela entidades
ALTER TABLE entidades 
    ADD COLUMN IF NOT EXISTS situacao VARCHAR(255) NULL,
    ADD COLUMN IF NOT EXISTS historico TEXT NULL,
    ADD COLUMN IF NOT EXISTS pa_emenda VARCHAR(255) NULL,
    ADD COLUMN IF NOT EXISTS localizacao_pa_emenda VARCHAR(255) NULL,
    ADD COLUMN IF NOT EXISTS emenda_alterada VARCHAR(100) NULL,
    ADD COLUMN IF NOT EXISTS pa_formalizacao VARCHAR(255) NULL,
    ADD COLUMN IF NOT EXISTS numero_emenda VARCHAR(100) NULL,
    ADD COLUMN IF NOT EXISTS vereador VARCHAR(255) NULL,
    ADD COLUMN IF NOT EXISTS justificativa TEXT NULL,
    ADD COLUMN IF NOT EXISTS valor NUMERIC(15, 2) NULL;

-- Comentários das novas colunas para documentação do banco
COMMENT ON COLUMN entidades.situacao IS 'Situação atual da formalização (Status, TSS, Em Análise, etc.)';
COMMENT ON COLUMN entidades.historico IS 'Registro cronológico de eventos e datas importantes';
COMMENT ON COLUMN entidades.pa_emenda IS 'Número do Processo Administrativo de Emenda';
COMMENT ON COLUMN entidades.localizacao_pa_emenda IS 'Localização física ou digital do PA de emenda';
COMMENT ON COLUMN entidades.emenda_alterada IS 'Indicação se a emenda sofreu alterações';
COMMENT ON COLUMN entidades.pa_formalizacao IS 'Número do Processo Administrativo de Formalização';
COMMENT ON COLUMN entidades.numero_emenda IS 'Número identificador da emenda parlamentar';
COMMENT ON COLUMN entidades.vereador IS 'Nome do vereador/parlamentar autor da emenda';
COMMENT ON COLUMN entidades.justificativa IS 'Justificativa social e técnica para a emenda';
COMMENT ON COLUMN entidades.valor IS 'Valor monetário total destinado à emenda/parceria';
