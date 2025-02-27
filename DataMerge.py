import os
import pandas as pd

# Specify the folder path
folder_path = "Final Project/Data/ERCOT SPPS"

# List to hold all filtered DataFrames
all_filtered_data = []

# Loop through all files in the folder
for filename in os.listdir(folder_path):
    full_path = os.path.join(folder_path, filename)
    
    if os.path.isfile(full_path) and filename.endswith('.xlsx'):
        print(f"Processing Excel file: {filename}")
        
        try:
            sheets = pd.read_excel(full_path, sheet_name=None)
            
            for sheet_name, df in sheets.items():
                print(f"Processing sheet: {sheet_name}")
                
                # Filter rows (replace 'Region' with your actual column name)
                filtered_df = df[df['Settlement Point Name'] == 'HB_NORTH']
                
                if not filtered_df.empty:
                    # Add source tracking columns (optional)
                    filtered_df['Source_File'] = filename
                    filtered_df['Source_Sheet'] = sheet_name
                    
                    # Append to the list
                    all_filtered_data.append(filtered_df)
                    print(f"Added {len(filtered_df)} rows from {sheet_name}")
                else:
                    print(f"No HB_NORTH rows in {sheet_name}")
        
        except Exception as e:
            print(f"Error processing {filename}: {e}")

# Combine all filtered DataFrames into one
if all_filtered_data:
    combined_df = pd.concat(all_filtered_data, ignore_index=True)
    
    # Save to a single CSV
    csv_full_path = os.path.join(folder_path, "All_HB_NORTH_Data.csv")
    combined_df.to_csv(csv_full_path, index=False)
    print(f"Saved {len(combined_df)} rows to: All_HB_NORTH_Data.csv")
else:
    print("No data found to save.")