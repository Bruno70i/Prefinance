-- DDL de Criacao da Tabela 'entidades'

-- Habilita a extensao para geracao de UUID se nao estiver ativa
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Criacao da tabela entidades
CREATE TABLE IF NOT EXISTS entidades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    razao_social VARCHAR(255) NOT NULL,
    cnpj VARCHAR(20) UNIQUE NULL,
    responsavel_nome VARCHAR(255) NULL,
    configuracoes_extras JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Comentarios explicativos da modelagem
COMMENT ON TABLE entidades IS 'Tabela principal contendo o cadastro basico e configuracoes de entidades/empresas do terceiro setor';
COMMENT ON COLUMN entidades.id IS 'Identificador unico da entidade gerado via UUID v4';
COMMENT ON COLUMN entidades.razao_social IS 'Nome oficial da Razao Social da entidade';
COMMENT ON COLUMN entidades.cnpj IS 'CNPJ unico da entidade formatado';
COMMENT ON COLUMN entidades.responsavel_nome IS 'Nome do gestor/responsavel direto da entidade';
COMMENT ON COLUMN entidades.configuracoes_extras IS 'Estrutura JSONB flexivel contendo atributos especificos (dados da parceria, metas detalhadas, historico de formalizacao)';

-- Funcao trigger para atualizar automaticamente o campo updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Criacao da trigger associada a tabela
DROP TRIGGER IF EXISTS update_entidades_updated_at ON entidades;
CREATE TRIGGER update_entidades_updated_at
    BEFORE UPDATE ON entidades
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
