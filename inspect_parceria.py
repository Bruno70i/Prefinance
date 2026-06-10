import pandas as pd
import json

file_path = r"d:\github\Prefinance\modelo\Planilhas_Consolidadas.xlsx"
xl = pd.ExcelFile(file_path)

# Sheet 2: DADOS DA PARCERIA
df2 = xl.parse('DADOS DA PARCERIA')
print("--- Sheet: DADOS DA PARCERIA ---")
for idx, row in df2.iterrows():
    # Print clean representation
    cleaned_row = {k: v for k, v in row.to_dict().items() if pd.notna(v)}
    print(f"Row {idx}: {cleaned_row}")
