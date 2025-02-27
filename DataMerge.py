import pandas as pd
import glob
import os


folder_path = "Data\ERCOT SPPS"


excel_files = glob.glob(os.path.join(folder_path, "*.xlsx"))
for excel_file in excel_files:
    # Read the Excel file
    df = pd.read_excel(excel_file, engine="openpyxl")

    # Define the output CSV file name (same name, but with .csv extension)
    csv_file = os.path.splitext(excel_file)[0] + ".csv"

    # Save as CSV
    df.to_csv(csv_file, index=False)

    print(f"Converted: {excel_file} -> {csv_file}")

