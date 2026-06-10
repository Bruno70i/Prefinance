-- Criação da tabela de dados da parceria relacionada à tabela de entidades (Relação 1:1/1:N)
CREATE TABLE IF NOT EXISTS dados_parceria (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entidade_id UUID NOT NULL UNIQUE REFERENCES entidades(id) ON DELETE CASCADE,
    ajuste_termo VARCHAR(255) NULL,
    inicio_atividades DATE NULL,
    termino_atividades DATE NULL,
    gestor_parceria VARCHAR(255) NULL,
    projeto VARCHAR(255) NULL,
    categorias JSONB DEFAULT '{}'::jsonb, -- Armazena booleanos das categorias selecionadas
    atendimento_descricao TEXT NULL,       -- Público alvo
    meta_mes_atendimentos INTEGER DEFAULT 0,
    responsavel_entidade VARCHAR(255) NULL,
    especialidades JSONB DEFAULT '{}'::jsonb, -- Especialidades dinâmicas e suas respectivas metas
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Comentários de documentação do banco
COMMENT ON TABLE dados_parceria IS 'Tabela relacionada contendo os termos de parceria, vigências e especialidades das entidades';
COMMENT ON COLUMN dados_parceria.entidade_id IS 'Chave estrangeira vinculando à entidade cadastrada (Relação 1:1/1:N)';
COMMENT ON COLUMN dados_parceria.categorias IS 'Categorias de atuação do fomento (Saúde Mental, Fisioterapia, etc.) salvas em formato JSONB';
COMMENT ON COLUMN dados_parceria.especialidades IS 'Especialidades ativas da parceria e suas metas em formato JSONB';
