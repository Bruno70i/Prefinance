import pandas as pd
import json
import math

file_path = r"d:\github\Prefinance\modelo\Planilhas_Consolidadas.xlsx"
xl = pd.ExcelFile(file_path)

def clean_val(val):
    if pd.isna(val):
        return None
    if isinstance(val, str):
        val = val.strip()
        return val if val else None
    return val

# ----------------- PARSING SHEET 1 (FORMALIZAÇÃO) -----------------
df1 = xl.parse('FORMALIZAÇÃO')
# The column headers are actually in row 0
headers1 = [clean_val(h) for h in df1.iloc[0]]
rows1 = df1.iloc[1:]

sheet1_data = []
for _, row in rows1.iterrows():
    row_dict = {}
    for col_idx, val in enumerate(row):
        col_name = headers1[col_idx]
        if col_name:
            row_dict[col_name] = clean_val(val)
    if row_dict.get('NOME'):
        sheet1_data.append(row_dict)

# ----------------- PARSING SHEET 2 (DADOS DA PARCERIA) -----------------
df2 = xl.parse('DADOS DA PARCERIA')
headers2 = [clean_val(h) for h in df2.iloc[0]]
rows2 = df2.iloc[1:]

sheet2_data = []
for _, row in rows2.iterrows():
    row_dict = {}
    for col_idx, val in enumerate(row):
        col_name = headers2[col_idx]
        # In headers2, some columns are None or Unnamed. We will use the raw column name from df2 if header is missing,
        # but row 0 has the actual fields: 'ENTIDADE', 'AJUSTE', 'INÍCIO DAS ATIVIDADES', 'TÉRMINO DAS ATIVIDADES', 'GESTOR DA PARCERIA', etc.
        # Let's inspect df2.columns and row 0
        raw_col = df2.columns[col_idx]
        if not col_name:
            col_name = clean_val(raw_col)
        if col_name:
            # We want to preserve unique sub-headers if possible.
            # Let's make sure we map correctly
            row_dict[col_name] = clean_val(val)
    
    # Handle the fact that some columns have duplicate names or empty names in row 0, let's map them by their standard positions
    # Row 0 values:
    # ENTIDADE: ENTIDADE, Unnamed 1: AJUSTE, Unnamed 2: INÍCIO DAS ATIVIDADES, Unnamed 3: TÉRMINO DAS ATIVIDADES,
    # Unnamed 4: GESTOR DA PARCERIA, Unnamed 5: PROJETO,
    # columns for projects: Saúde Mental, Fisioterapia, Fono, Animal, Outros
    # Unnamed 11: ATENDIMENTO, Unnamed 12: META (Mês)
    # Unnamed 13 to 41: Atendimentos específicos (Academia Clínica, Acupuntura, Fisioterapia, etc.)
    # Unnamed 42: RESPONSÁVEL PELA ENTIDADE, Unnamed 43: (also responsible or secondary name)
    # Let's write a precise extractor for Sheet 2:
    
    entidade_name = clean_val(row.iloc[0])
    if entidade_name:
        # Re-map clean fields
        meta_atendimentos = {}
        for c_idx in range(13, 42):
            col_label = clean_val(df2.iloc[0, c_idx])
            val_atend = clean_val(row.iloc[c_idx])
            if col_label and val_atend:
                meta_atendimentos[col_label] = val_atend
                
        projects = []
        for proj_idx in range(6, 11):
            proj_label = clean_val(df2.iloc[0, proj_idx])
            if clean_val(row.iloc[proj_idx]) == 'X' and proj_label:
                projects.append(proj_label)

        partner_dict = {
            'NOME': entidade_name,
            'AJUSTE': clean_val(row.iloc[1]),
            'INICIO_ATIVIDADES': clean_val(row.iloc[2]),
            'TERMINO_ATIVIDADES': clean_val(row.iloc[3]),
            'GESTOR': clean_val(row.iloc[4]),
            'PROJETO': clean_val(row.iloc[5]),
            'AREAS_PROJETO': projects,
            'PUBLICO_ATENDIMENTO': clean_val(row.iloc[11]),
            'META_MENSAL': clean_val(row.iloc[12]),
            'METAS_DETALHADAS': meta_atendimentos,
            'RESPONSAVEL_1': clean_val(row.iloc[42]),
            'RESPONSAVEL_2': clean_val(row.iloc[43]) if len(row) > 43 else None
        }
        sheet2_data.append(partner_dict)

# ----------------- PARSING SHEET 3 (REPASSE E PRESTAÇÃO) -----------------
df3 = xl.parse('REPASSE E PRESTAÇÃO DE CONTAS')
# Row 0 Col 1: Associação de Pais e Amigos dos Autistas de Guarujá - APAAG
# Row 1 Col 1: CNPJ: 04.211.135/0001-57
# Row 2 Col 1: CÓD. SCIM: 128409
# Row 3 Col 1: AJUSTE: TERMO DE CONVÊNIO 12/2024
# Row 4 Col 1: P.A. EMPENHO: 51369/2024
# Row 5 Col 1: OBJETO: TEA - Atendimentos...
# Let's extract this metadata
apaag_meta = {
    'NOME': 'Associação de Pais e Amigos dos Autistas de Guarujá - APAAG',
    'CNPJ': '04.211.135/0001-57',
    'COD_SCIM': '128409',
    'AJUSTE': 'TERMO DE CONVÊNIO 12/2024',
    'PA_EMPENHO': '51369/2024',
    'OBJETO': 'TEA - Atendimentos indicados à inclusão, reabilitação e tratamento de pessoas com diagnóstico ou hipótese diagnóstica de Transtorno do Espectro Autista e seus familiares, por meio de trabalho interdisciplinar de forma complementar aos serviços oferecidos para usuários do Sistema Único de Saúde no Município de Guarujá, de forma complementar ao Serviço Único de Saúde - SUS'
}

# ----------------- NORMALIZING & MERGING ENTITIES -----------------
# We have a few entities:
# 1. ASSOCIAÇÃO PARA A SAÚDE, CUIDADOS E EDUCAÇÃO SOCIAL SOBRE ANIMAIS - ASCESA (CNPJ: 33.695.684/0001-42)
# 2. ASSOCIAÇÃO ACOLHENDO VIDAS (CNPJ: 40.720.083/0001-08)
# 3. ASIPAVIC
# 4. ASSOCIAÇÃO DE PAIS E AMIGOS DOS AUTISTAS DE GUARUJÁ - APAAG (CNPJ: 04.211.135/0001-57)
# 5. ASSOCIAÇÃO DE PAIS E AMIGOS DOS EXCEPCIONAIS - APAE
# 6. ASSOCIAÇÃO EDUCANDO COM O SURF E A PRESERVAÇÃO AMBIENTAL - EDUCASURF

# Let's map everything to a unified Entity structure.
# Let's search by name overlaps
entities = {}

def get_or_create_entity(name):
    # Try to find existing entity by similar name
    norm_name = name.upper().strip()
    for key, ent in list(entities.items()):
        if norm_name in ent['razao_social'].upper() or ent['razao_social'].upper() in norm_name:
            return ent
    # If not found, create new
    new_ent = {
        'razao_social': name,
        'cnpj': None,
        'responsavel_nome': None,
        'configuracoes_extras': {}
    }
    entities[norm_name] = new_ent
    return new_ent

# 1. Load from Sheet 1 (Formalização)
for row1 in sheet1_data:
    ent = get_or_create_entity(row1['NOME'])
    ent['cnpj'] = row1.get('CNPJ')
    # Extra formalizacao config
    ent['configuracoes_extras']['formalizacao'] = {
        'status': row1.get('STATUS'),
        'historico': row1.get('HISTÓRICO'),
        'pa_emenda': row1.get('PA Emenda'),
        'localizacao_pa_emenda': row1.get('Localização do PA Emenda'),
        'emenda_alterada': row1.get('Emenda Alterada?'),
        'pa_formalizacao': row1.get('PA Formalização'),
        'numero': row1.get('N.º'),
        'vereador': row1.get('Vereador'),
        'justificativa': row1.get('Justificativa'),
        'valor': row1.get('Valor')
    }

# 2. Load from Sheet 2 (Dados da Parceria)
for row2 in sheet2_data:
    ent = get_or_create_entity(row2['NOME'])
    ent['responsavel_nome'] = row2['RESPONSAVEL_1'] or row2['RESPONSAVEL_2']
    ent['configuracoes_extras']['parceria'] = {
        'ajuste': row2.get('AJUSTE'),
        'inicio_atividades': row2.get('INICIO_ATIVIDADES'),
        'termino_atividades': row2.get('TERMINO_ATIVIDADES'),
        'gestor': row2.get('GESTOR'),
        'projeto': row2.get('PROJETO'),
        'areas_projeto': row2.get('AREAS_PROJETO'),
        'publico_atendimento': row2.get('PUBLICO_ATENDIMENTO'),
        'meta_mensal': row2.get('META_MENSAL'),
        'metas_detalhadas': row2.get('METAS_DETALHADAS')
    }
    if row2['RESPONSAVEL_2']:
        ent['configuracoes_extras']['responsavel_secundario'] = row2['RESPONSAVEL_2']

# 3. Add details from Sheet 3 (APAAG metadata)
apaag_ent = get_or_create_entity(apaag_meta['NOME'])
apaag_ent['cnpj'] = apaag_meta['CNPJ']
apaag_ent['configuracoes_extras']['financeiro_detalhes'] = {
    'codigo_scim': apaag_meta['COD_SCIM'],
    'ajuste_repasse': apaag_meta['AJUSTE'],
    'pa_empenho': apaag_meta['PA_EMPENHO'],
    'objeto': apaag_meta['OBJETO']
}

# Print output
final_list = list(entities.values())
output_json = json.dumps(final_list, indent=2, ensure_ascii=False)

with open(r"d:\github\Prefinance\entidades_mapeadas.json", "w", encoding="utf-8") as f:
    f.write(output_json)

print(output_json)
