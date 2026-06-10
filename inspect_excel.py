import pandas as pd
import json

file_path = r"d:\github\Prefinance\modelo\Planilhas_Consolidadas.xlsx"

try:
    xl = pd.ExcelFile(file_path)
    print("Sheets:", xl.sheet_names)
    
    for sheet_name in xl.sheet_names:
        df = xl.parse(sheet_name)
        print(f"\n--- Sheet: {sheet_name} ---")
        print("Shape:", df.shape)
        print("Columns:", list(df.columns))
        print("Head (2 rows):")
        print(df.head(2).to_dict(orient='records'))
except Exception as e:
    print("Error:", e)
