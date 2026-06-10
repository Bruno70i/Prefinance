import pandas as pd
import json

file_path = r"d:\github\Prefinance\modelo\Planilhas_Consolidadas.xlsx"
xl = pd.ExcelFile(file_path)

# Sheet 3: REPASSE E PRESTAÇÃO DE CONTAS
df3 = xl.parse('REPASSE E PRESTAÇÃO DE CONTAS')
print("--- Sheet: REPASSE E PRESTAÇÃO DE CONTAS ---")
for idx, row in df3.iterrows():
    cleaned_row = {k: v for k, v in row.to_dict().items() if pd.notna(v)}
    print(f"Row {idx}: {cleaned_row}")
