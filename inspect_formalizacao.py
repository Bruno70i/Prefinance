import pandas as pd
import json

file_path = r"d:\github\Prefinance\modelo\Planilhas_Consolidadas.xlsx"
xl = pd.ExcelFile(file_path)

# Sheet 1: FORMALIZAÇÃO
df1 = xl.parse('FORMALIZAÇÃO')
print("--- Sheet: FORMALIZAÇÃO ---")
# Print row index and rows
for idx, row in df1.iterrows():
    print(f"Row {idx}: {row.to_dict()}")
