import pandas as pd
import os

file_path = r"c:\Users\linkang\Downloads\节日集卡册数值 (2).xlsx"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit(1)

try:
    # Load the Excel file
    xls = pd.ExcelFile(file_path)
    sheet_names = xls.sheet_names
    
    with open("excel_analysis_v2.txt", "w", encoding="utf-8") as f:
        f.write(f"Sheet names: {sheet_names}\n")

        for sheet_name in sheet_names:
            f.write(f"\n--- Sheet: {sheet_name} ---\n")
            df = pd.read_excel(xls, sheet_name=sheet_name)
            f.write(f"Shape: {df.shape}\n")
            f.write("First 10 rows:\n")
            f.write(df.head(10).to_string())
            
            # Specific checks for "配置辅助"
            if sheet_name == "配置辅助":
                f.write("\n\nChecking Weights in Config Helper:\n")
                # Check rows 2-6 (indices 0-4 relative to data start usually, but let's just iterate rows)
                # Note: header is usually row 0 or 1.
                # Let's inspect the dataframe columns to identify weight columns.
                # Based on previous output: Unnamed: 3 is 1-star prob, Unnamed: 4 is 2-star...
                # Let's print the specific columns for rows that look like packs.
                
                # Iterate through rows and print relevant columns for manual/auto verification
                for index, row in df.iterrows():
                    f.write(f"\nRow {index}: {row.iloc[0]} - Weights: {row.iloc[3]} (1*), {row.iloc[4]} (2*), {row.iloc[5]} (3*), {row.iloc[6]} (4*), {row.iloc[7]} (5*)\n")
            
            f.write("\n")
            
    print("Analysis written to excel_analysis_v2.txt")

except Exception as e:
    print(f"Error reading Excel file: {e}")
